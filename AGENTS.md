# Repository Guidelines

## Competition Context
This repository targets Kaggle’s AI Mathematical Olympiad Progress Prize 3 (AIMO3). The task is to solve olympiad-level math problems and submit integer answers. The Kaggle evaluation uses an inference-style gateway that serves test problems one-by-one; the bundled `kaggle_evaluation` code sets a long runtime window and shuffles test order during public evaluation.
Current Kaggle listing (as of 2026-01-28): Featured competition, deadline 2026-04-15 23:59:00, reward 2,207,152 USD.

## Project Structure & Module Organization
- `data/raw/`: Kaggle downloads (`test.csv`, `sample_submission.csv`, `reference.csv`, `AIMO3_Reference_Problems.pdf`, `kaggle_evaluation/`).
- `data/processed/`: Cleaned or serialized problem datasets.
- `notebooks/`: EDA, prompt engineering, and analysis notebooks (e.g., `01-eda.ipynb`).
- `src/`: Core pipeline code (parsing, prompting, solvers, evaluation).
- `scripts/`: Reproducible CLI helpers (e.g., `baseline.py`).
- `models/`: Local checkpoints (keep out of Git).
- `submissions/`: CSV outputs for Kaggle.
- `docs/`: Competition notes and experiment logs.

## Build, Test, and Development Commands
- `python3 -m pip install -U kaggle pandas` — install Kaggle CLI and data tooling.
- `/Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle competitions download -c ai-mathematical-olympiad-progress-prize-3 -p data/raw` — download data.
- `unzip -o data/raw/ai-mathematical-olympiad-progress-prize-3.zip -d data/raw` — extract files.
- `python3 scripts/baseline.py` — generate a trivial submission (`submissions/baseline.csv`).
- `/Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle competitions submit -c ai-mathematical-olympiad-progress-prize-3 -f submissions/baseline.csv -m "baseline"` — submit.
- `/Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle competitions leaderboard -c ai-mathematical-olympiad-progress-prize-3 --show` — check leaderboard.

## Coding Style & Naming Conventions
- Python: 4-space indentation; `snake_case` for functions/variables, `PascalCase` for classes.
- Keep prompts and templates versioned in `src/` with descriptive names (e.g., `prompt_v1.py`).
- Notebooks: prefix with order and topic, e.g., `02-prompting.ipynb`.

## Testing Guidelines
No formal test suite yet. Add quick, deterministic unit tests in `tests/` (e.g., parser tests, answer normalization) and document how to run them.

## Commit & Pull Request Guidelines
If you initialize Git, use concise, imperative commit messages (e.g., “Add retrieval baseline”). PRs should include a short summary, experiment evidence, and links to relevant runs or notebooks.

## Security & Configuration Tips
Keep `kaggle.json` outside the repo (default: `~/.kaggle/kaggle.json`). Do not commit data, models, or submissions.
