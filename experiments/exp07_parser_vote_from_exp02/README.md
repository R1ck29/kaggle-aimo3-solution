# EXP07 wider parser + vote priority (from exp02 base)

## Objective
Widen answer extraction and prioritize vote count, isolated from speed profiling.

## Notebook
- `experiments/exp07_parser_vote_from_exp02/notebook.ipynb`

## Metadata
- `experiments/exp07_parser_vote_from_exp02/kernel-metadata.json`

## Changes
- branches from exp02 (score=40)
- _scan_for_answer: add answer=/answer:/final answer patterns
- _select_answer: sort by (votes, score)

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp07_parser_vote_from_exp02/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
