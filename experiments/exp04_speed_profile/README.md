# EXP04 + dynamic speed profile

## Objective
Adapt attempts/turns/early_stop by remaining per-question budget.

## Notebook
- `experiments/exp04_speed_profile/notebook.ipynb`

## Metadata
- `experiments/exp04_speed_profile/kernel-metadata.json`

## Changes
- inherits EXP03
- _process_attempt accepts turns argument
- add _select_speed_profile
- solve_problem uses dynamic attempts/turns/early_stop

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp04_speed_profile/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
