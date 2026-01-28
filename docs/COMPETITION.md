# AIMO3 Competition Summary

## Goal
Build a system that solves competition math problems and outputs a single integer answer per problem. Submissions are scored via Kaggle’s evaluation server.

## Competition Snapshot (via Kaggle CLI)
- Deadline: 2026-04-15 23:59:00
- Category: Featured
- Reward: 2,207,152 USD
- Team count (current): 1604

## Data Assets (downloaded to `data/raw/`)
- `test.csv` (3 rows, columns: `id`, `problem`): sample test problems.
- `sample_submission.csv` (3 rows, columns: `id`, `answer`): submission format template.
- `reference.csv` (10 rows, columns: `id`, `problem`, `answer`): tiny labeled set for sanity checks.
- `AIMO3_Reference_Problems.pdf`: reference problems PDF.
- `kaggle_evaluation/`: inference gateway code used during scoring.

## Evaluation Notes (from bundled gateway code)
- Test problems are served one-by-one in a randomized order for public scoring.
- A long runtime window is configured (9 hours), implying heavy inference is allowed.
- The official scoring logic lives on Kaggle’s evaluation service; use `sample_submission.csv` format.
For rules, exact metric definition, and submission limits, refer to the Kaggle competition page.

## Recommended Pipeline (adapted for AIMO3)
1. Install Kaggle API: `python3 -m pip install -U kaggle`.
2. Authenticate: place `kaggle.json` at `~/.kaggle/kaggle.json`.
3. Download data: `kaggle competitions download -c ai-mathematical-olympiad-progress-prize-3 -p data/raw`.
4. Unzip data: `unzip -o data/raw/ai-mathematical-olympiad-progress-prize-3.zip -d data/raw`.
5. Load data: `pandas.read_csv('data/raw/test.csv')`.
6. Inspect data: check `head()` and `info()`.
7. Preprocess: normalize problem text (strip, unify LaTeX tokens).
8. Feature/Prompt design: build structured prompts (e.g., chain-of-thought, tool use).
9. Target handling: answers are integers; normalize/validate outputs.
10. Local split: use `reference.csv` for quick validation; no official train split.
11. Model training/selection: choose LLM/prompting or symbolic solver components.
12. Local evaluation: compute exact-match on `reference.csv`.
13. Submission file: produce `submissions/*.csv` with `id,answer`.
14. Submit: `kaggle competitions submit -c ai-mathematical-olympiad-progress-prize-3 -f submissions/<file>.csv -m "msg"`.
15. Check results: `kaggle competitions leaderboard -c ai-mathematical-olympiad-progress-prize-3 --show`.

## Practical Tips
- Keep experiments reproducible (seeded decoding, logged prompts).
- Save model outputs and reasoning traces in `docs/` or `notebooks/`.
- Avoid committing `data/`, `models/`, or `submissions/` to Git.
