# Kaggle Status & Leaderboard Check

Check the status of all kernels and show the current leaderboard position.

## Instructions

1. Check the root kernel status:
   ```
   kaggle kernels status r1cky7/aimo-3-gpt-oss-120b-with-tools
   ```

2. Check each experiment kernel status by looking at what experiments exist:
   - List directories under `experiments/`
   - For each experiment that has a `kernel-metadata.json`, extract the `kernel_slug` and check its status
   - Report a summary table of all kernel statuses

3. Check the competition leaderboard:
   ```
   kaggle competitions leaderboard -c ai-mathematical-olympiad-progress-prize-3 --show
   ```

4. Present a summary showing:
   - Each kernel's current status (RUNNING, COMPLETE, ERROR, etc.)
   - Current best public score (38 from 2026-02-08)
   - Any pending submissions
   - Leaderboard position if visible

5. If any kernels are in ERROR state, suggest running `/kaggle-run` to investigate.
