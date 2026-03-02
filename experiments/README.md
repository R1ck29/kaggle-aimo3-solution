# Experiment Snapshots

Updated: 2026-03-02

This directory stores isolated experiment artifacts. Each experiment contains:
- `notebook.ipynb`
- `kernel-metadata.json`
- `README.md`

## V1 Experiments (Cumulative from V46)
- `exp01_workers_batch` — workers 16→8, batch 256→128
- `exp02_token_cap` — + per-turn token cap 12288 (**score: 40**)
- `exp03_parser_vote` — + wider parser + vote-priority sort (score: 38)
- `exp04_speed_profile` — + dynamic speed profiling (score: PENDING)

## V2 Experiments (Non-cumulative, branching from exp02)
- `exp05_more_attempts` — attempts 8→16, early_stop 4→8, workers 8→16
- `exp06_prompt_verify` — verification prompt
- `exp07_parser_vote_from_exp02` — wider parser + vote sort (isolated)
- `exp08_combined_best` — all combined + batch 256

## Run Example
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp05_more_attempts/kernel-metadata.json \
  --download-output always
```
