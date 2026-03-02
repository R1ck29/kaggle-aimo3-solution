# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Competition Context

Kaggle AIMO3 (AI Mathematical Olympiad Progress Prize 3). Solve olympiad-level math problems, submit integer answers. Featured competition, deadline 2026-04-15, $2.2M reward. Best public score: 40 (exp02_token_cap, as of 2026-02-23).

## Evaluation Constraints

- Test problems are served **one-by-one in randomized order** during public scoring
- Runtime window: **9 hours** on H100 GPU — heavy inference is expected
- Submission format: `id,answer` (integer answers only)
- Submission mode: **code competition** — must submit kernel, not CSV/parquet directly
- Parquet direct upload returns `400 Bad Request`; use `kaggle kernels push` with code submission flow

## Architecture

**Inference pipeline** runs inside a Kaggle kernel on H100 GPU:
- Model: GPT-OSS-120B via vLLM (bundled as `gpt-oss-120b.tar.gz`)
- Strategy: multi-attempt reasoning → per-turn token cap (12,288) → answer parsing → majority-vote consensus
- Dynamic speed profiling adapts attempts/turns based on remaining time budget
- Reliability wrappers: auto-discover model paths, wheels archive, and test CSV under `/kaggle/input`

**Key files:**
- `notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb` — main submission notebook (V46 kernel source)
- `kernel-metadata.json` — Kaggle kernel config (H100, private, internet disabled)
- `scripts/kaggle_kernel_run.py` — push/run/poll kernels with auto-staging of experiment metadata
- `scripts/create_experiment_notebooks.py` — generate isolated ablation notebooks via cell-index patching
- `experiments/` — isolated experiment snapshots (exp01-exp08) with run logs and outputs
- `docs/` — competition rules, experiment log, gap analysis, workflow guides

## Notebook Cell Map

The V46 notebook (`_v6.ipynb`) has 17 cells (0-indexed):

| Cell | Role | Key Content |
|------|------|-------------|
| 0 | CLEANUP | `%pip uninstall` keras/matplotlib/sklearn/tensorflow |
| 1 | WARNINGS | `warnings.simplefilter('ignore')` |
| 2 | IMPORTS_SYS | `os`, `sys`, `subprocess` |
| 3 | **SETUP** | `set_env()` — extract wheels, install deps |
| 4 | SETUP_CALL | `set_env(input_archive=..., temp_dir=...)` |
| 5 | VERIFY | `ls tiktoken_encodings` |
| 6 | ENV_VARS | Transformer env vars |
| 7 | IMPORTS_ML | `gc`, `re`, `math`, ML imports |
| 8 | **CFG** | `class CFG` — all hyperparameters |
| 9 | SEED | `set_seed(CFG.seed)` |
| 10 | TEMPLATE | `class AIMO3Template` |
| 11 | SANDBOX | `class AIMO3Sandbox` |
| 12 | TOOL | `class AIMO3Tool` |
| 13 | **SOLVER** | `class AIMO3Solver` — vLLM engine, reasoning loop |
| 14 | SOLVER_INIT | `solver = AIMO3Solver(CFG)` |
| 15 | PREDICT | `def predict(...)` — gateway callback |
| 16 | **GATEWAY** | `kaggle_evaluation` inference server start |

When patching experiments, target cells by index. Critical cells: SETUP=3, CFG=8, SOLVER=13, GATEWAY=16.

## Known V46 Diffs (Score 38 Config vs Current Base)

The V46 config that scored 38 differs from the current base notebook:

| Parameter | V46 (score 38) | Current base |
|-----------|----------------|--------------|
| `model_path` | `/kaggle/input/gpt-oss-120b/transformers/default/1` | `/kaggle/input/gpt-oss-120b-eagle3-throughput` |
| `dtype` | `auto` | `float16` |
| `kv_cache_dtype` | `fp8_e4m3` | `fp16` |
| `top_logprobs` | `5` | `0` |
| `batch_size` | `256` | `64` |
| `attempts` | `8` | `4` |
| `turns` | `128` | `64` |
| `early_stop` | `4` | `3` |
| `temperature` | `1.0` | `0.7` |

Control flow diffs:
- V46: hard H100 assert (`_assert_h100_environment`) / Current: soft disable fallback
- V46: eager solver init / Current: lazy init with lock
- V46: fixed attempts/turns / Current: dynamic speed profile
- V46: no archive precheck (fails at tar) / Current: strict archive existence check

## Experiment Rules

### Cumulative Patching
- All experiments are built from the V46 base (`_v6.ipynb`) via cell-index patching
- Patches are cumulative: each experiment includes all reliability fixes plus its specific ablation
- Use `scripts/create_experiment_notebooks.py` to generate experiment notebooks programmatically

### Shared Reliability Patches (3 functions)
All experiment notebooks must include these to avoid known failures:
1. `resolve_input_archive()` — discovers `wheels.tar.gz` under `/kaggle/input/**`
2. `CFG.resolve_model_path()` — discovers valid model dir containing `config.json`
3. `resolve_test_csv_path()` — discovers competition `test.csv` under both old/new mount layouts

### Isolation
- Each experiment lives in `experiments/<exp_key>/` with its own notebook, `kernel-metadata.json`, and `README.md`
- Run via: `python3 scripts/kaggle_kernel_run.py --metadata experiments/<exp_key>/kernel-metadata.json --download-output always`

## Kernel Debugging Runbook

### Failure Pattern: wheels.tar.gz not found
- **Symptom**: `tar: /kaggle/input/aimo-3-utils/wheels.tar.gz: Cannot open`
- **Fix**: Use `resolve_input_archive()` instead of hardcoded path

### Failure Pattern: config.json not found
- **Symptom**: `OSError: Can't load the configuration of '...'` or `FileNotFoundError: config.json not found`
- **Fix**: Use `CFG.resolve_model_path()` to walk filesystem and find valid model dir

### Failure Pattern: test.csv path mismatch
- **Symptom**: `FileNotFoundError: .../test.csv`
- **Fix**: Use `resolve_test_csv_path()` to search both old and new Kaggle mount layouts

### Failure Pattern: Direct parquet submission
- **Symptom**: `400 Bad Request` from `kaggle competitions submit`
- **Fix**: This is a code competition — submit via `kaggle kernels push` not direct file upload

### Failure Pattern: gRPC metadata limit
- **Symptom**: `RESOURCE_EXHAUSTED metadata > 8192`
- **Context**: Historical issue with eagle3-throughput model on T4 GPU; resolved by switching to H100 + gpt-oss-120b

### H100 Verification Checklist
1. `kernel-metadata.json` has `"machine_shape": "NvidiaH100"`
2. `model_sources` uses full format: `danielhanchen/gpt-oss-120b/transformers/default/1`
3. After push, verify: `kaggle kernels pull r1cky7/aimo-3-gpt-oss-120b-with-tools -p /tmp/aimo3_kernel_check -m`
4. In logs, confirm: `Detected GPU: NVIDIA H100`

## AIMO2 Reference Patterns

Key lessons from AIMO2 Fast-Math-R1 applicable to AIMO3:
1. **SFT→RL two-stage**: SFT improves accuracy but increases length; RL (GRPO) reduces token usage
2. **Token-budget-aware inference**: Large accuracy drop-offs at reduced budgets (8k vs 16k)
3. **Question-level early stopping**: Stop when majority consensus emerges (e.g., 5/7 agree)
4. **Dynamic speed profiling**: Reduce samples/max-length when time per remaining question < threshold
5. **Early termination at `</think>`**: Answer often appears before closing tag
6. **Inference stack tuning**: vLLM + quantization + KV cache as first-order optimization knobs

## Common Commands

```bash
# Push and run the root kernel on Kaggle
python3 scripts/kaggle_kernel_run.py

# Push and run a specific experiment kernel
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp02_token_cap/kernel-metadata.json \
  --download-output always

# Check kernel status
kaggle kernels status r1cky7/aimo-3-gpt-oss-120b-with-tools

# Check leaderboard
kaggle competitions leaderboard -c ai-mathematical-olympiad-progress-prize-3 --show

# Generate experiment notebooks from base
python3 scripts/create_experiment_notebooks.py

# Push to GitHub (requires GITHUB_PAT and GITHUB_REPO env vars)
./scripts/push_github.sh
```

## Coding Style

- Python: 4-space indentation, `snake_case` for functions/variables, `PascalCase` for classes
- No formal test suite; `tests/` directory exists but is empty
- Notebook cells are the primary development unit — changes often require cell-index patching

## Key Patterns

- **Metadata staging**: `kaggle_kernel_run.py` copies experiment-specific `kernel-metadata.json` to the root before pushing, ensuring the Kaggle CLI reads the correct config
- **Experiment isolation**: each experiment gets its own notebook + metadata + README, generated programmatically from the base notebook
- **Path resilience**: notebook code walks `/kaggle/input` to find model weights, wheels archive, and test CSV regardless of mount layout changes
- **Kaggle kernel constraints**: H100 GPU, 9-hour runtime, no internet, private kernel

## Data & Model Files (git-ignored)

`data/`, `models/`, `submissions/`, `*.zip`, `kaggle.json` are all in `.gitignore`. The model tarball `gpt-oss-120b.tar.gz` is tracked but large (~5GB).
