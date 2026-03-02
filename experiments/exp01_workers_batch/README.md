# EXP01 workers/batch alignment

## Objective
Align worker count with attempt count and lower max_num_seqs pressure.

## Notebook
- `experiments/exp01_workers_batch/notebook.ipynb`

## Metadata
- `experiments/exp01_workers_batch/kernel-metadata.json`

## Changes
- workers: 16 -> 8
- batch_size(max-num-seqs): 256 -> 128

## Run
```bash
python3 scripts/kaggle_kernel_run.py \
  --metadata experiments/exp01_workers_batch/kernel-metadata.json \
  --download-output always
```

## Result
- Status: TODO
- Public score: TODO
- Notes: TODO
