# Experiment TODO (Target: Public Score > 40, Goal 43+)

Updated: 2026-03-02

## Execution Rules
- Run experiments in order: `exp01` -> `exp02` -> `exp03` -> `exp04`.
- Keep each experiment isolated under `experiments/<exp_key>/`.
- Download outputs for every run and record the exact log path.
- Update both this file and `docs/EXPERIMENT_LOG.md` after each experiment.

## Global TODO
- [x] Reconnect Kaggle CLI execution path (network requires escalated commands in this environment).
- [x] Create per-experiment directories and notebook snapshots.
- [x] Fix `scripts/kaggle_kernel_run.py` so `--metadata` is actually staged for `kaggle kernels push`.
- [x] Confirm root kernel failure cause from log (missing `/kaggle/input/aimo-3-utils/wheels.tar.gz`).
- [x] Add wheels archive auto-discovery in experiment notebooks (`resolve_input_archive`).
- [x] Confirm `exp02` second failure cause from log (invalid fixed model path for vLLM startup).
- [x] Add model path auto-discovery in experiment notebooks (`CFG.resolve_model_path`).
- [x] Correct `model_sources` case to `.../Transformers/default/1` in metadata.
- [x] Add competition `test.csv` auto-discovery for local gateway (`resolve_test_csv_path`).
- [x] Wait for `exp02` latest run completion and record status.
- [x] Run `exp03_parser_vote` after `exp02` completion.
- [x] Run `exp04_speed_profile` after `exp03` completion.
- [x] Wait for `exp04` completion and collect outputs.
- [x] Use code-competition submission mode (`-k/-v/-f`) instead of uploading local parquet directly.
- [x] Identify `V46` artifact and compare it with latest pulled kernel artifact.
- [x] Pull `V46` logs and confirm failure reason from raw log.
- [x] Wait for `exp02_v9_code_submit` to move from `PENDING` to `COMPLETE`. → **Score: 40**
- [x] Submit `exp03` to leaderboard (2026-03-01, PENDING)
- [x] Wait for exp03 score (38), then submit exp04 (PENDING)
- [x] Push and run exp05-exp08 on Kaggle (all COMPLETE)
- [ ] Submit exp05-exp08 as code competition entries (blocked by exp04 PENDING)
- [ ] Compare completed public scores and pick next base

## Experiment Matrix (V1 — Cumulative from V46)
| Experiment | Hypothesis | Status | Public Score |
|---|---|---|---|
| exp01_workers_batch | Reduce overhead: workers 16→8, batch 256→128 | DONE (older build) | N/A |
| exp02_token_cap | + per-turn token cap 12288 | COMPLETE (v9) | **40** |
| exp03_parser_vote | + wider parser + vote-priority sort | COMPLETE (v1) | **38** |
| exp04_speed_profile | + dynamic speed profiling | COMPLETE (v1) | PENDING |
| v46_reference | V46 baseline | ANALYZED | 38 |

## Experiment Matrix (V2 — Branching from exp02, score=40)
| Experiment | Hypothesis | Kernel Status | Public Score |
|---|---|---|---|
| exp05_more_attempts | attempts 8→16, early_stop 4→8, workers 8→16 | COMPLETE | Not yet submitted |
| exp06_prompt_verify | verification prompt | COMPLETE | Not yet submitted |
| exp07_parser_vote_v2 | wider parser + vote sort (no speed profile) | COMPLETE | Not yet submitted |
| exp08_combined_best | all combined + batch 256 | COMPLETE | Not yet submitted |

## Reference Runs
- Root kernel ERROR log:
  - `experiments/base_runs/20260215_230513/aimo-3-gpt-oss-120b-with-tools.log`
- V46 pulled output log:
  - `/private/tmp/aimo3_v46_output/aimo-3-gpt-oss-120b-with-tools.log`
- `exp02` latest run directory:
  - `experiments/exp02_token_cap/runs/20260218_212221/` (COMPLETE)
- `exp03` latest run directory:
  - `experiments/exp03_parser_vote/runs/20260218_213203/` (COMPLETE)
- `exp04` latest run directory:
  - `experiments/exp04_speed_profile/runs/20260218_222608/` (COMPLETE)

## V46 Isolation TODO (Deprioritized)
Previous plan for V46 isolation ablations (exp05-exp09) replaced by V2 experiments branching from exp02 (score=40).

## Run Command Template
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/<exp_key>/kernel-metadata.json \
  --kaggle-bin /Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle \
  --download-output always
```
