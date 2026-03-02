#!/usr/bin/env python3
"""Create staged AIMO3 experiment notebooks and metadata files.

Experiments are cumulative and built from:
notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb
"""
from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
BASE_NOTEBOOK = ROOT / "notebooks" / "aimo-3-gpt-oss-120b-with-tools _v6.ipynb"
BASE_METADATA = ROOT / "kernel-metadata.json"
EXPERIMENTS_ROOT = ROOT / "experiments"
KERNEL_OWNER = "r1cky7"

SETUP_CELL_INDEX = 3
CFG_CELL_INDEX = 8
SOLVER_CELL_INDEX = 13
GATEWAY_CELL_INDEX = 16


@dataclass(frozen=True)
class ExperimentSpec:
    key: str
    title: str
    summary: str
    changes: list[str]
    apply: Callable[[str, str], tuple[str, str]]


def to_lines(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Expected snippet not found for {label}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, repl: str, label: str) -> str:
    # Use a lambda replacement so backslashes in notebook code are treated literally.
    new_text, count = re.subn(pattern, lambda _m: repl, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Regex replacement failed for {label}")
    return new_text


def patch_shared_setup(setup: str) -> str:
    setup = replace_once(
        setup,
        "def set_env(input_archive, temp_dir):\n",
        "def resolve_input_archive(input_archive):\n"
        "\n"
        "    if os.path.exists(input_archive):\n"
        "        return input_archive\n"
        "\n"
        "    for root, _, files in os.walk('/kaggle/input'):\n"
        "        if 'wheels.tar.gz' in files:\n"
        "            return os.path.join(root, 'wheels.tar.gz')\n"
        "\n"
        "    raise FileNotFoundError(\n"
        "        f\"wheels.tar.gz not found under /kaggle/input (default={input_archive})\"\n"
        "    )\n"
        "\n"
        "\n"
        "def set_env(input_archive, temp_dir):\n",
        "shared setup resolver",
    )
    setup = replace_once(
        setup,
        "        subprocess.run(['tar', '-xzf', input_archive, '-C', temp_dir], check=True)\n",
        "        archive_path = resolve_input_archive(input_archive)\n"
        "        print(f'Using archive: {archive_path}')\n"
        "        subprocess.run(['tar', '-xzf', archive_path, '-C', temp_dir], check=True)\n",
        "shared setup archive resolution",
    )
    return setup


def patch_shared_cfg(cfg: str) -> str:
    cfg = replace_once(
        cfg,
        "    served_model_name = 'gpt-oss'\n    model_path = '/kaggle/input/gpt-oss-120b/transformers/default/1'\n",
        "    served_model_name = 'gpt-oss'\n"
        "    model_path = '/kaggle/input/gpt-oss-120b/transformers/default/1'\n"
        "    model_root = '/kaggle/input/gpt-oss-120b'\n"
        "    input_root = '/kaggle/input'\n"
        "\n"
        "    @classmethod\n"
        "    def resolve_model_path(cls) -> str:\n"
        "        preferred_paths = [\n"
            "            cls.model_path,\n"
            "            '/kaggle/input/gpt-oss-120b/Transformers/default/1',\n"
            "            '/kaggle/input/gpt-oss-120b/transformers/default/1',\n"
        "        ]\n"
        "\n"
        "        for path in preferred_paths:\n"
        "            if os.path.exists(os.path.join(path, 'config.json')):\n"
        "                return path\n"
        "\n"
        "        for root, _, files in os.walk(cls.input_root):\n"
        "            if 'config.json' in files:\n"
        "                return root\n"
        "\n"
        "        available_sources = []\n"
        "        if os.path.exists(cls.input_root):\n"
        "            available_sources = sorted(os.listdir(cls.input_root))\n"
        "\n"
        "        raise FileNotFoundError(\n"
        "            'config.json not found under /kaggle/input. '\n"
        "            f'available sources: {available_sources}'\n"
        "        )\n",
        "shared cfg model path resolution",
    )
    return cfg


def patch_shared_solver(solver: str) -> str:
    solver = replace_once(
        solver,
        "        self.cfg = cfg\n"
        "        self.port = port\n",
        "        self.cfg = cfg\n"
        "        self.cfg.model_path = self.cfg.resolve_model_path()\n"
        "        print(f'Using model path: {self.cfg.model_path}')\n"
        "        self.port = port\n",
        "shared solver resolved model path",
    )
    return solver


def patch_shared_gateway(gateway: str) -> str:
    gateway = replace_once(
        gateway,
        "inference_server = kaggle_evaluation.aimo_3_inference_server.AIMO3InferenceServer(predict)\n"
        "\n"
        "if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):\n"
        "    inference_server.serve()\n"
        "    \n"
        "else:\n"
        "    inference_server.run_local_gateway(\n"
        "        ('/kaggle/input/ai-mathematical-olympiad-progress-prize-3/test.csv',)\n"
        "    )",
        "def resolve_test_csv_path() -> str:\n"
        "    candidates = [\n"
        "        '/kaggle/input/ai-mathematical-olympiad-progress-prize-3/test.csv',\n"
        "        '/kaggle/input/competitions/ai-mathematical-olympiad-progress-prize-3/test.csv',\n"
        "    ]\n"
        "\n"
        "    for path in candidates:\n"
        "        if os.path.exists(path):\n"
        "            return path\n"
        "\n"
        "    for root, _, files in os.walk('/kaggle/input'):\n"
        "        if root.endswith('/ai-mathematical-olympiad-progress-prize-3') and 'test.csv' in files:\n"
        "            return os.path.join(root, 'test.csv')\n"
        "\n"
        "    for root, _, files in os.walk('/kaggle/input'):\n"
        "        if 'test.csv' in files and 'sample_submission.csv' in files:\n"
        "            return os.path.join(root, 'test.csv')\n"
        "\n"
        "    raise FileNotFoundError('test.csv for AIMO3 competition not found under /kaggle/input')\n"
        "\n"
        "\n"
        "inference_server = kaggle_evaluation.aimo_3_inference_server.AIMO3InferenceServer(predict)\n"
        "\n"
        "if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):\n"
        "    inference_server.serve()\n"
        "\n"
        "else:\n"
        "    test_csv_path = resolve_test_csv_path()\n"
        "    print(f'Using test.csv: {test_csv_path}')\n"
        "    inference_server.run_local_gateway((test_csv_path,))",
        "shared gateway test path resolution",
    )
    return gateway


def exp01_workers_batch(cfg: str, solver: str) -> tuple[str, str]:
    cfg = replace_once(cfg, "    batch_size = 256\n", "    batch_size = 128\n", "exp01 batch_size")
    cfg = replace_once(cfg, "    workers = 16\n", "    workers = 8\n", "exp01 workers")
    return cfg, solver


def exp02_token_cap(cfg: str, solver: str) -> tuple[str, str]:
    cfg = replace_once(
        cfg,
        "    context_tokens = 65536\n",
        "    context_tokens = 65536\n    max_tokens_per_turn = 12288\n",
        "exp02 max_tokens_per_turn",
    )
    solver = replace_once(
        solver,
        "                max_tokens = self.cfg.context_tokens - len(prompt_ids)\n",
        "                context_left = self.cfg.context_tokens - len(prompt_ids)\n"
        "                max_tokens = min(context_left, self.cfg.max_tokens_per_turn)\n",
        "exp02 generation cap",
    )
    return cfg, solver


def exp03_parser_vote(cfg: str, solver: str) -> tuple[str, str]:
    scan_block = """    def _scan_for_answer(self, text: str) -> int | None:\n        \n        patterns = [\n            r'\\\\boxed\\s*\\{\\s*([0-9,]+)\\s*\\}',\n            r'answer\\s*(?:is|=|:)\\s*([0-9,]+)',\n            r'final\\s+answer\\s*(?:is|=|:)\\s*([0-9,]+)',\n        ]\n\n        for pattern in patterns:\n            matches = re.findall(pattern, text, re.IGNORECASE)\n\n            if not matches:\n                continue\n\n            try:\n                clean_value = matches[-1].replace(',', '')\n                value = int(clean_value)\n\n                if 0 <= value <= 99999:\n                    return value\n\n            except ValueError:\n                continue\n\n        return None\n"""

    solver = replace_regex_once(
        solver,
        r"    def _scan_for_answer\(self, text: str\) -> int \| None:\n.*?        return None\n",
        scan_block,
        "exp03 scan_for_answer",
    )

    solver = replace_once(
        solver,
        "        scored_answers.sort(key=lambda x: x['score'], reverse=True)\n",
        "        scored_answers.sort(key=lambda x: (x['votes'], x['score']), reverse=True)\n",
        "exp03 vote priority",
    )
    return cfg, solver


def exp04_speed_profile(cfg: str, solver: str) -> tuple[str, str]:
    solver = replace_once(
        solver,
        "        deadline: float\n    ) -> dict:\n",
        "        deadline: float,\n        turns: int\n    ) -> dict:\n",
        "exp04 process_attempt signature",
    )
    solver = replace_once(
        solver,
        "            for _ in range(self.cfg.turns):\n",
        "            for _ in range(turns):\n",
        "exp04 turns arg",
    )

    speed_method = """    def _select_speed_profile(self, avg_time_per_question: float) -> tuple[int, int, int]:\n        # Adjust attempts/turns based on remaining time per question.\n        if avg_time_per_question < 300:\n            return 4, 64, 3\n        if avg_time_per_question < 600:\n            return 6, 96, 3\n        return self.cfg.attempts, self.cfg.turns, self.cfg.early_stop\n\n"""

    solver = replace_once(
        solver,
        "    def _select_answer(self, detailed_results: list) -> int:\n",
        speed_method + "    def _select_answer(self, detailed_results: list) -> int:\n",
        "exp04 insert speed profile",
    )

    solve_method = """    def solve_problem(self, problem: str) -> int:\n\n        print(f'\\nProblem: {problem}\\n')\n        \n        user_input = f'{problem} {self.cfg.preference_prompt}'\n\n        elapsed_global = time.time() - self.notebook_start_time\n        time_left = self.cfg.notebook_limit - elapsed_global\n        problems_left_others = max(0, self.problems_remaining - 1)\n        reserved_time = problems_left_others * self.cfg.base_problem_timeout\n\n        budget = time_left - reserved_time\n        budget = min(budget, self.cfg.high_problem_timeout)\n        budget = max(budget, self.cfg.base_problem_timeout)\n\n        deadline = time.time() + budget\n\n        print(f'Budget: {budget:.2f} seconds | Deadline: {deadline:.2f}\\n')\n        avg_time_per_question = time_left / max(self.problems_remaining, 1)\n        attempts, turns, early_stop = self._select_speed_profile(avg_time_per_question)\n        print(f'Speed profile: attempts={attempts}, turns={turns}, early_stop={early_stop}\\n')\n\n        tasks = []\n\n        for attempt_index in range(attempts):\n            tasks.append((self.cfg.system_prompt, attempt_index))\n\n        detailed_results = []\n        valid_answers = []\n\n        stop_event = threading.Event()\n\n        executor = ThreadPoolExecutor(max_workers=self.cfg.workers)\n\n        try:\n            futures = []\n\n            for (system_prompt, attempt_index) in tasks:\n                future = executor.submit(\n                    self._process_attempt, \n                    user_input, \n                    system_prompt, \n                    attempt_index, \n                    stop_event, \n                    deadline,\n                    turns\n                )\n\n                futures.append(future)\n\n            for future in as_completed(futures):\n                try:\n                    result = future.result()\n                    detailed_results.append(result)\n\n                    if result['Answer'] is not None:\n                        valid_answers.append(result['Answer'])\n\n                    counts = Counter(valid_answers).most_common(1)\n\n                    if counts and counts[0][1] >= early_stop:\n                        stop_event.set()\n\n                        for f in futures:\n                            f.cancel()\n\n                        break\n\n                except Exception as exc:\n                    print(f'Future failed: {exc}')\n                    continue\n\n        finally:\n            stop_event.set()\n            executor.shutdown(wait=True, cancel_futures=True)\n            \n            self.problems_remaining = max(0, self.problems_remaining - 1)\n\n        if detailed_results:\n            results_dataframe = pd.DataFrame(detailed_results)\n            results_dataframe['Entropy'] = results_dataframe['Entropy'].round(3)\n            results_dataframe['Answer'] = results_dataframe['Answer'].astype('Int64')\n            \n            display(results_dataframe)\n\n        if not valid_answers:\n            print('\\nResult: 0\\n')\n\n            return 0\n\n        return self._select_answer(detailed_results)\n"""

    solver = replace_regex_once(
        solver,
        r"    def solve_problem\(self, problem: str\) -> int:\n.*?        return self._select_answer\(detailed_results\)\n",
        solve_method,
        "exp04 solve_problem",
    )
    return cfg, solver


def exp05_more_attempts(cfg: str, solver: str) -> tuple[str, str]:
    cfg = replace_once(cfg, "    attempts = 8\n", "    attempts = 16\n", "exp05 attempts")
    cfg = replace_once(cfg, "    early_stop = 4\n", "    early_stop = 8\n", "exp05 early_stop")
    cfg = replace_once(cfg, "    workers = 8\n", "    workers = 16\n", "exp05 workers")
    return cfg, solver


def exp06_prompt_verify(cfg: str, solver: str) -> tuple[str, str]:
    cfg = replace_once(
        cfg,
        "    system_prompt = (\n"
        "        'You are a world-class International Mathematical Olympiad (IMO) competitor. '\n"
        "        'The final answer must be a non-negative integer between 0 and 99999. '\n"
        "        'You must place the final integer answer inside \\\\boxed{}.'\n"
        "    )\n",
        "    system_prompt = (\n"
        "        'You are a world-class International Mathematical Olympiad (IMO) competitor. '\n"
        "        'The final answer must be a non-negative integer between 0 and 99999. '\n"
        "        'You must place the final integer answer inside \\\\boxed{}. '\n"
        "        'After reasoning, verify your answer by writing Python code. '\n"
        "        'Only place your final integer in \\\\boxed{} after verification.'\n"
        "    )\n",
        "exp06 system_prompt",
    )
    cfg = replace_once(
        cfg,
        "    preference_prompt = (\n"
        "        'You have access to `math`, `numpy` and `sympy` to solve the problem.'\n"
        "    )\n",
        "    preference_prompt = (\n"
        "        'You have access to `math`, `numpy` and `sympy` to solve the problem. '\n"
        "        'Always double-check your answer with code before finalizing.'\n"
        "    )\n",
        "exp06 preference_prompt",
    )
    return cfg, solver


def exp07_parser_vote_from_exp02(cfg: str, solver: str) -> tuple[str, str]:
    """Apply only the exp03 parser/vote changes on top of exp02 state."""
    return exp03_parser_vote(cfg, solver)


def exp08_combined_best(cfg: str, solver: str) -> tuple[str, str]:
    """Apply all improvements: more attempts + prompt verify + parser/vote."""
    cfg, solver = exp05_more_attempts(cfg, solver)
    cfg, solver = exp06_prompt_verify(cfg, solver)
    cfg, solver = exp07_parser_vote_from_exp02(cfg, solver)
    # Restore batch_size to 256 (H100 has headroom with 16 attempts)
    cfg = replace_once(cfg, "    batch_size = 128\n", "    batch_size = 256\n", "exp08 batch_size")
    return cfg, solver


SPECS: list[ExperimentSpec] = [
    ExperimentSpec(
        key="exp01_workers_batch",
        title="EXP01 workers/batch alignment",
        summary="Align worker count with attempt count and lower max_num_seqs pressure.",
        changes=[
            "workers: 16 -> 8",
            "batch_size(max-num-seqs): 256 -> 128",
        ],
        apply=exp01_workers_batch,
    ),
    ExperimentSpec(
        key="exp02_token_cap",
        title="EXP02 + per-turn token cap",
        summary="Cap per-turn generation tokens to reduce long-tail outputs.",
        changes=[
            "inherits EXP01",
            "add CFG.max_tokens_per_turn = 12288",
            "max_tokens = min(context_left, max_tokens_per_turn)",
        ],
        apply=exp02_token_cap,
    ),
    ExperimentSpec(
        key="exp03_parser_vote",
        title="EXP03 + parser/vote update",
        summary="Widen answer extraction patterns and prioritize vote count in aggregation.",
        changes=[
            "inherits EXP02",
            "_scan_for_answer: add answer=/answer:/final answer patterns",
            "_select_answer: sort by (votes, score)",
        ],
        apply=exp03_parser_vote,
    ),
    ExperimentSpec(
        key="exp04_speed_profile",
        title="EXP04 + dynamic speed profile",
        summary="Adapt attempts/turns/early_stop by remaining per-question budget.",
        changes=[
            "inherits EXP03",
            "_process_attempt accepts turns argument",
            "add _select_speed_profile",
            "solve_problem uses dynamic attempts/turns/early_stop",
        ],
        apply=exp04_speed_profile,
    ),
]


# V2 experiments branch from exp02 state (shared patches + exp01 + exp02).
# Each applies ONE additional change, non-cumulative.
SPECS_V2: list[ExperimentSpec] = [
    ExperimentSpec(
        key="exp05_more_attempts",
        title="EXP05 more attempts (from exp02 base)",
        summary="Increase parallel reasoning attempts for better consensus on hard problems.",
        changes=[
            "branches from exp02 (score=40)",
            "attempts: 8 -> 16",
            "early_stop: 4 -> 8",
            "workers: 8 -> 16",
        ],
        apply=exp05_more_attempts,
    ),
    ExperimentSpec(
        key="exp06_prompt_verify",
        title="EXP06 enhanced prompt with verification (from exp02 base)",
        summary="Encourage code verification before finalizing answers.",
        changes=[
            "branches from exp02 (score=40)",
            "system_prompt: add verification instruction",
            "preference_prompt: add double-check instruction",
        ],
        apply=exp06_prompt_verify,
    ),
    ExperimentSpec(
        key="exp07_parser_vote_from_exp02",
        title="EXP07 wider parser + vote priority (from exp02 base)",
        summary="Widen answer extraction and prioritize vote count, isolated from speed profiling.",
        changes=[
            "branches from exp02 (score=40)",
            "_scan_for_answer: add answer=/answer:/final answer patterns",
            "_select_answer: sort by (votes, score)",
        ],
        apply=exp07_parser_vote_from_exp02,
    ),
    ExperimentSpec(
        key="exp08_combined_best",
        title="EXP08 combined best improvements (from exp02 base)",
        summary="Combine all promising changes: more attempts + verification prompt + wider parser.",
        changes=[
            "branches from exp02 (score=40)",
            "attempts: 8 -> 16, early_stop: 4 -> 8, workers: 8 -> 16",
            "system_prompt + preference_prompt: verification instructions",
            "wider parser + vote priority",
            "batch_size: 128 -> 256 (H100 headroom)",
        ],
        apply=exp08_combined_best,
    ),
]


def render_experiment_readme(spec: ExperimentSpec, notebook_rel: str, metadata_rel: str) -> str:
    change_lines = "\n".join(f"- {item}" for item in spec.changes)
    return f"""# {spec.title}

## Objective
{spec.summary}

## Notebook
- `{notebook_rel}`

## Metadata
- `{metadata_rel}`

## Changes
{change_lines}

## Run
```bash
python3 scripts/kaggle_kernel_run.py \\
  --metadata {metadata_rel} \\
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
"""


def write_experiment(
    base_nb: dict,
    base_meta: dict,
    spec: ExperimentSpec,
    setup_text: str,
    cfg_text: str,
    solver_text: str,
    gateway_text: str,
    index: int,
    total: int,
) -> None:
    exp_dir = EXPERIMENTS_ROOT / spec.key
    exp_dir.mkdir(parents=True, exist_ok=True)

    notebook_path = exp_dir / "notebook.ipynb"
    metadata_path = exp_dir / "kernel-metadata.json"
    readme_path = exp_dir / "README.md"

    nb = copy.deepcopy(base_nb)
    nb["cells"][SETUP_CELL_INDEX]["source"] = to_lines(setup_text)
    nb["cells"][CFG_CELL_INDEX]["source"] = to_lines(cfg_text)
    nb["cells"][SOLVER_CELL_INDEX]["source"] = to_lines(solver_text)
    nb["cells"][GATEWAY_CELL_INDEX]["source"] = to_lines(gateway_text)
    notebook_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n")

    meta = copy.deepcopy(base_meta)
    kernel_slug = spec.key.replace("_", "-")
    meta["id"] = f"{KERNEL_OWNER}/aimo3-{kernel_slug}"
    meta["title"] = f"AIMO3 {spec.key}"
    meta["code_file"] = "notebook.ipynb"
    metadata_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    readme_path.write_text(
        render_experiment_readme(
            spec,
            str(notebook_path.relative_to(ROOT)),
            str(metadata_path.relative_to(ROOT)),
        )
    )

    print(f"[{index}/{total}] wrote {notebook_path}")


def main() -> None:
    EXPERIMENTS_ROOT.mkdir(parents=True, exist_ok=True)

    base_nb = json.loads(BASE_NOTEBOOK.read_text())
    base_meta = json.loads(BASE_METADATA.read_text())

    setup_text = "".join(base_nb["cells"][SETUP_CELL_INDEX]["source"])
    cfg_text = "".join(base_nb["cells"][CFG_CELL_INDEX]["source"])
    solver_text = "".join(base_nb["cells"][SOLVER_CELL_INDEX]["source"])
    gateway_text = "".join(base_nb["cells"][GATEWAY_CELL_INDEX]["source"])
    setup_text = patch_shared_setup(setup_text)
    cfg_text = patch_shared_cfg(cfg_text)
    solver_text = patch_shared_solver(solver_text)
    gateway_text = patch_shared_gateway(gateway_text)

    total = len(SPECS) + len(SPECS_V2)

    # --- V1: cumulative experiments (exp01 -> exp02 -> exp03 -> exp04) ---
    for index, spec in enumerate(SPECS, start=1):
        cfg_text, solver_text = spec.apply(cfg_text, solver_text)
        write_experiment(base_nb, base_meta, spec, setup_text, cfg_text, solver_text, gateway_text, index, total)

        # Save exp02 checkpoint for V2 experiments
        if spec.key == "exp02_token_cap":
            exp02_cfg = cfg_text
            exp02_solver = solver_text

    # --- V2: non-cumulative experiments branching from exp02 ---
    for index, spec in enumerate(SPECS_V2, start=len(SPECS) + 1):
        v2_cfg, v2_solver = spec.apply(exp02_cfg, exp02_solver)
        write_experiment(base_nb, base_meta, spec, setup_text, v2_cfg, v2_solver, gateway_text, index, total)


if __name__ == "__main__":
    main()
