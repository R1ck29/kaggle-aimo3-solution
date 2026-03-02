#!/usr/bin/env python3
import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

STATUS_RE = re.compile(r'status "(?P<status>[A-Za-z0-9_\.]+)"')


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if check and proc.returncode != 0:
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        parts = [f"Command failed ({proc.returncode}): {' '.join(cmd)}"]
        if stdout:
            parts.append(f"STDOUT:\n{stdout}")
        if stderr:
            parts.append(f"STDERR:\n{stderr}")
        raise RuntimeError("\n".join(parts))
    return proc


def load_metadata(metadata_path: Path) -> dict:
    return json.loads(metadata_path.read_text())


@contextlib.contextmanager
def stage_metadata_for_push(metadata_path: Path, push_path: Path):
    """Ensure Kaggle reads the requested metadata file during `kernels push`.

    Kaggle CLI only reads `<push_path>/kernel-metadata.json`, so we temporarily
    stage the selected metadata there when needed.
    """
    push_metadata = push_path / 'kernel-metadata.json'
    same_file = push_metadata.resolve() == metadata_path.resolve()
    if same_file:
        yield
        return

    original = push_metadata.read_bytes() if push_metadata.exists() else None
    push_metadata.write_bytes(metadata_path.read_bytes())
    try:
        yield
    finally:
        if original is None:
            with contextlib.suppress(FileNotFoundError):
                push_metadata.unlink()
        else:
            push_metadata.write_bytes(original)


def parse_status(output: str) -> str:
    match = STATUS_RE.search(output)
    if not match:
        return "UNKNOWN"
    return match.group('status')


def download_output(kaggle_bin: str, kernel_id: str, output_dir: str, *, show_log: bool = False) -> None:
    run([kaggle_bin, 'kernels', 'output', kernel_id, '-p', output_dir, '--force'], check=False)
    if show_log:
        log_path = Path(output_dir) / f"{kernel_id.split('/')[-1]}.log"
        if log_path.exists():
            size = log_path.stat().st_size
            with open(log_path, 'rb') as f:
                f.seek(max(0, size - 4000))
                print(f.read().decode(errors='replace'))
            return
    print(f"Downloaded output to {output_dir}")


def should_retry_network_error(message: str) -> bool:
    markers = (
        "NameResolutionError",
        "Max retries exceeded",
        "ConnectionError",
        "ReadTimeout",
        "Temporary failure in name resolution",
        "nodename nor servname provided",
    )
    return any(marker in message for marker in markers)


def main() -> int:
    parser = argparse.ArgumentParser(description="Push and run a Kaggle kernel, then watch for completion.")
    parser.add_argument('--metadata', default='kernel-metadata.json', help='Path to kernel-metadata.json')
    parser.add_argument('--kernel-id', help='Kernel id, overrides metadata id')
    parser.add_argument('--push-path', help='Directory to push (defaults to metadata parent, else current dir)')
    parser.add_argument('--kaggle-bin', default=os.environ.get('KAGGLE_BIN', 'kaggle'), help='Kaggle CLI path')
    parser.add_argument(
        '--accelerator',
        default='NvidiaH100',
        help='Accelerator id for push (project policy: NvidiaH100)',
    )
    parser.add_argument('--push', action='store_true', default=True, help='Push kernel before running')
    parser.add_argument('--no-push', dest='push', action='store_false')
    parser.add_argument('--wait', action='store_true', default=True, help='Wait for completion')
    parser.add_argument('--no-wait', dest='wait', action='store_false')
    parser.add_argument('--poll-interval', type=int, default=30, help='Seconds between status checks')
    parser.add_argument('--timeout', type=int, default=3600, help='Max seconds to wait')
    parser.add_argument('--command-retries', type=int, default=5, help='Retry count for transient network failures')
    parser.add_argument('--command-retry-wait', type=int, default=5, help='Seconds to wait between command retries')
    parser.add_argument('--download-output', choices=['on_error', 'always', 'never'], default='on_error')
    parser.add_argument('--output-dir', default='/tmp/aimo-kernel-output', help='Where to download logs/outputs')
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    if not metadata_path.exists() and not args.kernel_id:
        print(f"metadata not found: {metadata_path}", file=sys.stderr)
        return 2

    metadata = load_metadata(metadata_path) if metadata_path.exists() else {}
    kernel_id = args.kernel_id or metadata.get('id')
    if not kernel_id:
        print(f"No kernel id found (metadata={metadata_path})", file=sys.stderr)
        return 2
    push_path = Path(args.push_path) if args.push_path else (metadata_path.parent if metadata_path.exists() else Path('.'))
    if args.push and not push_path.exists():
        print(f"push path not found: {push_path}", file=sys.stderr)
        return 2

    if args.push and metadata:
        code_file = metadata.get('code_file')
        if code_file:
            code_path = push_path / code_file
            if not code_path.exists():
                print(
                    f"code_file not found from push path: {code_path} "
                    f"(metadata={metadata_path}, push_path={push_path})",
                    file=sys.stderr,
                )
                return 2

    def run_with_retries(cmd: list[str], label: str) -> subprocess.CompletedProcess:
        for attempt in range(args.command_retries + 1):
            try:
                return run(cmd, check=True)
            except RuntimeError as exc:
                msg = str(exc)
                if attempt >= args.command_retries or not should_retry_network_error(msg):
                    raise
                wait_s = args.command_retry_wait
                print(
                    f"[retry {attempt + 1}/{args.command_retries}] {label} failed with network error; "
                    f"sleeping {wait_s}s...",
                    file=sys.stderr,
                )
                time.sleep(wait_s)
        raise RuntimeError(f"Unexpected retry flow for {label}")

    if args.push:
        try:
            metadata_ctx = (
                stage_metadata_for_push(metadata_path, push_path)
                if metadata_path.exists()
                else contextlib.nullcontext()
            )
            with metadata_ctx:
                push = run_with_retries(
                    [args.kaggle_bin, 'kernels', 'push', '-p', str(push_path), '--accelerator', args.accelerator],
                    "kernels push",
                )
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(push.stdout.strip())
        if push.stderr.strip():
            print(push.stderr.strip(), file=sys.stderr)

    if not args.wait:
        return 0

    start = time.time()
    status = "UNKNOWN"

    while time.time() - start < args.timeout:
        try:
            result = run_with_retries([args.kaggle_bin, 'kernels', 'status', kernel_id], "kernels status")
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        status = parse_status(result.stdout)
        print(result.stdout.strip())

        if status in {"KernelWorkerStatus.COMPLETE", "COMPLETE"}:
            if args.download_output == 'always':
                download_output(args.kaggle_bin, kernel_id, args.output_dir)
            return 0

        if status in {"KernelWorkerStatus.ERROR", "ERROR"}:
            if args.download_output in {'on_error', 'always'}:
                download_output(args.kaggle_bin, kernel_id, args.output_dir, show_log=True)
            return 1

        time.sleep(args.poll_interval)

    print(f"Timed out after {args.timeout} seconds. Last status: {status}")
    return 3


if __name__ == '__main__':
    raise SystemExit(main())
