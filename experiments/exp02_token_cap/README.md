# EXP02 + per-turn token cap

## Objective
Cap per-turn generation tokens to reduce long-tail outputs.

## Notebook
- `experiments/exp02_token_cap/notebook.ipynb`

## Metadata
- `experiments/exp02_token_cap/kernel-metadata.json`

## Changes
- inherits EXP01
- add CFG.max_tokens_per_turn = 12288
- max_tokens = min(context_left, max_tokens_per_turn)

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp02_token_cap/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
