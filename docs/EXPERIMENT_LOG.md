# Experiment Log

## Historical
- 2026-01-29T08:45 (trial1, ver28): model=gpt-oss-120b-eagle3-throughput, float16, attempts=6, turns=80, top_logprobs=0, batch_size=64, stream_interval=200 -> ERROR (RESOURCE_EXHAUSTED metadata > 8192)
- 2026-01-29T09:10 (trial2, ver29): same model, attempts=4, turns=48, batch_size=64, stream_interval=400, temperature=0.7, top_logprobs=0 -> ERROR (RESOURCE_EXHAUSTED metadata > 8192)
- 2026-01-29T09:45 (trial3, ver30): dataset_sources fixed (model only), attempts=4, turns=64, batch_size=64, stream_interval=200, temperature=0.7 -> ERROR (RESOURCE_EXHAUSTED metadata > 8192)

Notes:
- GPU was T4 (capability 60) in those runs; mxfp4 quant models were unusable.
- Eagle3-throughput (no quant) still hit gRPC metadata soft limit on Kaggle evaluation.

## 2026-02-15 Experiment Series (Target: >38)

### Preparation
- Created isolated experiment directories:
  - `experiments/exp01_workers_batch/`
  - `experiments/exp02_token_cap/`
  - `experiments/exp03_parser_vote/`
  - `experiments/exp04_speed_profile/`
- Added generator: `scripts/create_experiment_notebooks.py`
- Added execution helper: `scripts/kaggle_kernel_run.py`

### Connectivity and Tooling
- Sandbox-only Kaggle calls failed with DNS resolution errors to `api.kaggle.com`.
- Kaggle commands executed successfully with escalated permissions.
- `scripts/kaggle_kernel_run.py` fixed to stage the selected `--metadata` file into push path so `kaggle kernels push` uses the intended metadata.

### Root-Cause Findings (Confirmed from Logs)
1. Root kernel (`r1cky7/aimo-3-gpt-oss-120b-with-tools`) failed with:
   - `tar: /kaggle/input/aimo-3-utils/wheels.tar.gz: Cannot open`
   - Log: `experiments/base_runs/20260215_230513/aimo-3-gpt-oss-120b-with-tools.log`
2. `exp02` run (v5) progressed past setup, then failed at vLLM startup because fixed model path was invalid in that runtime:
   - `OSError: Can't load the configuration of '/kaggle/input/gpt-oss-120b/transformers/default/1'`
   - Log: `experiments/exp02_token_cap/runs/20260215_225711/aimo3-exp02-token-cap.log`
3. `exp02` run (v6) failed with:
   - `FileNotFoundError: config.json not found under /kaggle/input/gpt-oss-120b`
   - Confirmed model source was not mounted with lowercase metadata path.
   - Log: `experiments/exp02_token_cap/runs/20260215_230717/aimo3-exp02-token-cap.log`
4. `exp02` run (v8) reached model startup but failed in local gateway with:
   - `FileNotFoundError: /kaggle/input/ai-mathematical-olympiad-progress-prize-3/test.csv`
   - Log: `experiments/exp02_token_cap/runs/20260218_211218/aimo3-exp02-token-cap.log`

### Mitigations Added
- Added `resolve_input_archive()` to discover `wheels.tar.gz` under `/kaggle/input/**`.
- Added `CFG.resolve_model_path()` to discover a valid model directory containing `config.json` under `/kaggle/input/**`.
- Added solver initialization line to use the resolved model path and print it.
- Updated metadata `model_sources` to `danielhanchen/gpt-oss-120b/Transformers/default/1` (uppercase `Transformers`).
- Added `resolve_test_csv_path()` to discover competition `test.csv` under both old and new Kaggle mount layouts.

### Execution Status
- `exp01_workers_batch` (older build): completed previously, log available at `experiments/exp01_workers_batch/runs/20260215_222348/aimo3-exp01-workers-batch.log`
- `exp02_token_cap` latest:
  - push: kernel version 9
  - status: `COMPLETE` (2026-02-18 21:31 JST)
  - run dir: `experiments/exp02_token_cap/runs/20260218_212221/`
  - output files: `submission.parquet`, `vllm_server.log`, `aimo3-exp02-token-cap.log`
  - runtime evidence: model resolved to `/kaggle/input/models/danielhanchen/gpt-oss-120b/transformers/default/1` and H100 detected
- `exp03_parser_vote`:
  - push: kernel version 1
  - status: `COMPLETE` (2026-02-18 21:41 JST)
  - run dir: `experiments/exp03_parser_vote/runs/20260218_213203/`
  - output files: `submission.parquet`, `vllm_server.log`, `aimo3-exp03-parser-vote.log`
- `exp04_speed_profile`:
  - push: kernel version 1
  - status: `COMPLETE` (2026-02-18 22:33 JST)
  - run dir: `experiments/exp04_speed_profile/runs/20260218_222608/`
  - output files: `submission.parquet`, `vllm_server.log`, `aimo3-exp04-speed-profile.log`

### Submission Check
- Tried submitting `exp02` output file:
  - command: `kaggle competitions submit -c ai-mathematical-olympiad-progress-prize-3 -f experiments/exp02_token_cap/runs/20260218_212221/submission.parquet -m "exp02_token_cap_v9"`
  - result: `400 Client Error: Bad Request`
- Competition submission board remains unchanged after the attempt:
  - latest complete submission is still dated `2026-02-08` with public score `38`.

## 2026-02-23 V46 Gap Confirmation

### Artifact identity (hash-level)
- Pulled `V46`:
  - `/private/tmp/aimo3_v46_check/aimo-3-gpt-oss-120b-with-tools.ipynb`
- Pulled latest:
  - `/private/tmp/aimo3_latest_check/aimo-3-gpt-oss-120b-with-tools.ipynb`
- File hashes are identical:
  - notebook: `a245512c91a0897727dbadfa2de0b249beb8ff9b6cafd659409dcb7372e5f122`
  - metadata: `d4a2dd43bf4c8514030f6d9b57369801ae95c0cb26213b6fe742938097493ddd`
- Code-cell hash confirms:
  - pulled `V46` == pulled latest == local `notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb`
  - local `notebooks/aimo-3-gpt-oss-120b-with-tools.ipynb` is different code.

### V46 runtime status
- `kaggle kernels status r1cky7/aimo-3-gpt-oss-120b-with-tools/46`
  - `KernelWorkerStatus.ERROR`
- Pulled log (`/private/tmp/aimo3_v46_output/aimo-3-gpt-oss-120b-with-tools.log`) shows setup failure:
  - missing `/kaggle/input/aimo-3-utils/wheels.tar.gz`
  - `CalledProcessError` in `set_env(...)`.

### Current submission state
- `2026-02-08 12:44:20`: description `V6?`, `COMPLETE`, public `38`
- `2026-02-23 13:59:08`: `exp02_v9_code_submit`, `PENDING`

### Difference summary (V46 code vs current variants)
- V46 and current root notebook differ on:
  - model path, dtype/kv cache, attempts/turns, top_logprobs, temperature
  - hard H100 check vs soft-disable fallback
  - eager solver init vs lazy solver init
  - fixed strategy vs dynamic speed profile
- Experiments (`exp01`..`exp04`) are V46-based with reliability patches plus targeted ablations.

### Reference
- Full detailed evidence: `docs/V46_GAP_ANALYSIS.md`

## 2026-03-02 Score Confirmation and New Experiments

### exp02 Score Confirmed
- `exp02_v9_code_submit` public score: **40** (up from 38 baseline)
- Submitted 2026-02-23, completed and scored

### exp03 Submitted
- Submitted `exp03_parser_vote` as code competition entry (2026-03-01)
- Status: PENDING

### exp04 Submission Blocked
- Cannot submit while exp03 is PENDING (only one pending submission allowed)
- Will submit after exp03 completes

### New Experiment Series (V2, branching from exp02 = score 40)
Created exp05-exp08, each branching independently from exp02 state:

| Experiment | Change | Hypothesis |
|---|---|---|
| exp05_more_attempts | attempts 8→16, early_stop 4→8, workers 8→16 | More parallel attempts → better consensus |
| exp06_prompt_verify | Enhanced system/preference prompt with verification instruction | Code verification before finalizing → fewer wrong answers |
| exp07_parser_vote_from_exp02 | Wider parser + vote-priority sort (exp03 changes only) | Isolate parser/vote improvement from speed profiling |
| exp08_combined_best | All of above + batch_size 128→256 | Combined improvements for maximum effect |

All notebooks generated via `scripts/create_experiment_notebooks.py`.

### Kernel Execution Status (2026-03-02)
- exp05_more_attempts: pushed v1, COMPLETE, output downloaded to `/tmp/aimo3-exp05-output/`
- exp06_prompt_verify: pushed v1, COMPLETE, output downloaded to `/tmp/aimo3-exp06-output/`
- exp07_parser_vote_v2: pushed v1, RUNNING (renamed slug from `parser-vote-from-exp02` due to push error)
- exp08_combined_best: pushed v1, RUNNING

### Leaderboard Results
- exp03_parser_vote: **38** (no improvement over V46 baseline — wider parser + vote sort did NOT help)
- exp04_speed_profile: PENDING (submitted 2026-03-02)

### Kernel Completion
- exp07_parser_vote_v2: COMPLETE, output downloaded to `/tmp/aimo3-exp07-output/`
- exp08_combined_best: COMPLETE, output downloaded to `/tmp/aimo3-exp08-output/`

### Notes
- Kaggle limit: max 2 concurrent GPU sessions
- exp07 original slug `aimo3-exp07-parser-vote-from-exp02` failed with "Notebook not found"; shortened to `aimo3-exp07-parser-vote-v2`
- exp03 scored 38, same as V46 — wider parser may be matching false positives or vote-priority sort is hurting when some attempts produce wrong answers with high vote counts
