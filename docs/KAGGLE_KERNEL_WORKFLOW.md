# Kaggle Kernel Run Workflow

This repo uses a Kaggle notebook kernel defined in `kernel-metadata.json`. The script below pushes the notebook and waits for completion, downloading logs if it fails.

## Prerequisites

- Kaggle CLI installed and authenticated (`~/.kaggle/kaggle.json`).
- Notebook path and kernel id in `kernel-metadata.json` are correct.

## Quick Run

```bash
scripts/kaggle_kernel_run.py
```

What it does:
- `kaggle kernels push -p <metadata directory>`
- Polls status until COMPLETE or ERROR
- On ERROR, downloads logs to `/tmp/aimo-kernel-output` and prints the tail

## H100 Fixed Runbook (2026-02-08)

Use this checklist to avoid the recent failure pattern.

1. Keep Kaggle CLI updated.

```bash
python3 -m pip install -U kaggle
```

2. Use model source in full model-instance-version format.

```json
"model_sources": ["danielhanchen/gpt-oss-120b/Transformers/default/1"]
```

3. Push with the documented accelerator id (`NvidiaH100`).

```bash
kaggle kernels push -p . --accelerator NvidiaH100
```

4. Verify server-side metadata after push.

```bash
kaggle kernels pull r1cky7/aimo-3-gpt-oss-120b-with-tools -p /tmp/aimo3_kernel_check -m
cat /tmp/aimo3_kernel_check/kernel-metadata.json
```

Expected:
- `"machine_shape": "NvidiaH100"`
- `model_sources` contains `.../transformers/default/1`

5. Verify runtime GPU from logs.

```bash
kaggle kernels output r1cky7/aimo-3-gpt-oss-120b-with-tools -p /tmp/aimo-kernel-output --force
grep -n "Detected GPU" /tmp/aimo-kernel-output/aimo-3-gpt-oss-120b-with-tools.log | tail -n 1
```

Expected:
- `Detected GPU: NVIDIA H100 ...`

If this shows `P100/T4/L4`, treat it as environment allocation mismatch and rerun with explicit `--accelerator NvidiaH100`.


## Run Experiment Metadata

Use a per-experiment metadata file to keep runs isolated:

```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp01_workers_batch/kernel-metadata.json \
  --download-output always
```

Repeat by replacing `exp01_workers_batch` with any experiment key (exp02-exp08).

Note:
- `scripts/kaggle_kernel_run.py` now stages the selected `--metadata` as `<push_path>/kernel-metadata.json` before push, so Kaggle uses the intended metadata.

## Common Options

```bash
# Use a different kernel id
scripts/kaggle_kernel_run.py --kernel-id r1cky7/aimo-3-gpt-oss-120b-with-tools

# Change polling interval / timeout
scripts/kaggle_kernel_run.py --poll-interval 15 --timeout 7200

# Always download output (even on success)
scripts/kaggle_kernel_run.py --download-output always

# Skip push (only poll status)
scripts/kaggle_kernel_run.py --no-push
```

## Troubleshooting

- **Kernel ERROR with vLLM config.json missing**
  - Check `CFG.model_path` in the notebook.
  - Run a quick `ls /kaggle/input/...` in a Kaggle session to confirm the correct path.

- **Authentication errors**
  - Ensure `~/.kaggle/kaggle.json` exists and has correct permissions.

- **Kernel stuck RUNNING**
  - Increase `--timeout` or check kernel logs in the Kaggle UI.

## Notes

- The script uses `KAGGLE_BIN` if set; otherwise it runs `kaggle` from your PATH.
- Logs are stored at `/tmp/aimo-kernel-output/<kernel-slug>.log`.
