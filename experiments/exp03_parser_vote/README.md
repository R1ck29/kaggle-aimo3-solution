# EXP03 + parser/vote update

## Objective
Widen answer extraction patterns and prioritize vote count in aggregation.

## Notebook
- `experiments/exp03_parser_vote/notebook.ipynb`

## Metadata
- `experiments/exp03_parser_vote/kernel-metadata.json`

## Changes
- inherits EXP02
- _scan_for_answer: add answer=/answer:/final answer patterns
- _select_answer: sort by (votes, score)

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp03_parser_vote/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
