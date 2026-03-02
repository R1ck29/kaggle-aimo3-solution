# Kaggle Kernel Push & Run

Push and run a Kaggle kernel, then poll until completion and show results.

## Instructions

1. Determine which kernel to run:
   - If the user provided an experiment name (e.g., "exp02_token_cap"), use: `python3 scripts/kaggle_kernel_run.py --metadata experiments/<exp_name>/kernel-metadata.json --download-output always`
   - If no argument provided, run the root kernel: `python3 scripts/kaggle_kernel_run.py --download-output always`

2. Run the command and wait for output. The script handles:
   - Staging the correct kernel-metadata.json
   - Pushing via `kaggle kernels push`
   - Polling status until COMPLETE or ERROR
   - Downloading output on ERROR

3. After the run completes:
   - If COMPLETE: report success, show any output files found
   - If ERROR: download and display the tail of the log file, then check the error against known patterns:
     - `wheels.tar.gz` not found → needs `resolve_input_archive()`
     - `config.json` not found → needs `CFG.resolve_model_path()`
     - `test.csv` not found → needs `resolve_test_csv_path()`
   - Suggest fixes based on the debugging runbook in CLAUDE.md

4. After a successful run, remind the user to check leaderboard: `kaggle competitions leaderboard -c ai-mathematical-olympiad-progress-prize-3 --show`

## Arguments
$ARGUMENTS - Optional: experiment name (e.g., "exp02_token_cap") or full metadata path
