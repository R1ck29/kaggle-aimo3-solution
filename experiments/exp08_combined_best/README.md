# EXP08 combined best improvements (from exp02 base)

## Objective
Combine all promising changes: more attempts + verification prompt + wider parser.

## Notebook
- `experiments/exp08_combined_best/notebook.ipynb`

## Metadata
- `experiments/exp08_combined_best/kernel-metadata.json`

## Changes
- branches from exp02 (score=40)
- attempts: 8 -> 16, early_stop: 4 -> 8, workers: 8 -> 16
- system_prompt + preference_prompt: verification instructions
- wider parser + vote priority
- batch_size: 128 -> 256 (H100 headroom)

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp08_combined_best/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
