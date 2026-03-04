# AIMO3 Project Handover

Updated: 2026-03-04

## 1. What Is This

Kaggle AIMO3 (AI Mathematical Olympiad Progress Prize 3) competition entry.
- **Goal**: Solve olympiad-level math problems → integer answers
- **Prize**: $2.2M total, deadline **2026-04-15**
- **Hardware**: H100 GPU, 9-hour runtime, no internet
- **Model**: GPT-OSS-120B served via vLLM
- **Strategy**: Multi-attempt reasoning → token-capped generation → answer parsing → majority vote

## 2. Current Standing

| Metric | Value |
|--------|-------|
| **Best public score** | **40** (exp02_token_cap, submitted 2026-02-23) |
| Previous best | 38 (V46 "V6?", 2026-02-08) |
| Leaderboard top | ~45 |
| Target | 43+ (TOP10) |
| Gap to close | 3-5 more problems correct out of ~50 |

## 3. What's Happening Right Now

### Pending Submission
- **exp04_speed_profile** was submitted as a code competition entry on **2026-03-02 04:09 UTC**
- Status: **PENDING** (Kaggle re-runs the full 9-hour kernel for scoring)
- This has been pending for ~48 hours — may be in a long scoring queue

### Blocked Items
- **Cannot submit exp05-exp08** until exp04 clears (Kaggle allows only 1 pending submission at a time)
- Submission queue after exp04: **exp05 → exp06** (most promising), then optionally exp07/exp08

### All Kernels Are Ready
All 8 experiment kernels are `COMPLETE` on Kaggle and ready for leaderboard submission:

| Experiment | Kernel Slug | Kernel Status | Leaderboard |
|---|---|---|---|
| exp02_token_cap | `r1cky7/aimo3-exp02-token-cap` (v9) | COMPLETE | **40** |
| exp03_parser_vote | `r1cky7/aimo3-exp03-parser-vote` (v1) | COMPLETE | **38** |
| exp04_speed_profile | `r1cky7/aimo3-exp04-speed-profile` (v1) | COMPLETE | **PENDING** |
| exp05_more_attempts | `r1cky7/aimo3-exp05-more-attempts` (v1) | COMPLETE | Not submitted |
| exp06_prompt_verify | `r1cky7/aimo3-exp06-prompt-verify` (v1) | COMPLETE | Not submitted |
| exp07_parser_vote_v2 | `r1cky7/aimo3-exp07-parser-vote-v2` (v1) | COMPLETE | Not submitted |
| exp08_combined_best | `r1cky7/aimo3-exp08-combined-best` (v1) | COMPLETE | Not submitted |

## 4. What We Learned (Key Findings)

### What worked (+2 points, 38→40)
- **exp02_token_cap**: Per-turn token cap (12288), batch_size 128, workers 8
- Token cap prevents runaway generation and keeps attempts within time budget

### What did NOT work (38, same as baseline)
- **exp03_parser_vote**: Wider answer parser + vote-priority sorting
- Wider parser may match false positives
- Vote-priority sort may amplify wrong answers when multiple attempts converge on a wrong answer
- **This is the single most important finding** — exp07 and exp08 include the same parser/vote changes, so they may also regress

### Unknown (not yet scored)
- **exp04**: Dynamic speed profiling (reduce attempts/turns when running low on time)
- **exp05**: More attempts (8→16) — most promising if time budget allows
- **exp06**: Verification prompt ("verify with code before finalizing") — promising if model follows instruction
- **exp07**: Parser/vote changes isolated from exp02 — likely to regress (same changes as exp03)
- **exp08**: All combined — includes parser/vote changes, so may be dragged down

### Strategic Priority
1. **exp05** (more attempts) — pure scaling, no risky changes
2. **exp06** (verification prompt) — low-risk prompt improvement
3. exp04 (speed profiling) — already submitted, awaiting score
4. exp07/exp08 — lower priority due to parser/vote regression risk

## 5. Experiment Architecture

### Two generations of experiments

**V1 (Cumulative)**: Each builds on the previous
```
V46 base → exp01 (workers/batch) → exp02 (token cap) → exp03 (parser/vote) → exp04 (speed profile)
```

**V2 (Non-cumulative)**: Each branches from exp02 independently
```
exp02 (score=40) → exp05 (more attempts)
exp02 (score=40) → exp06 (verification prompt)
exp02 (score=40) → exp07 (parser/vote, isolated)
exp02 (score=40) → exp08 (all combined)
```

### Score-40 Config (exp02, the current best)
```python
# Key hyperparameters
model_path = auto-discovered via resolve_model_path()
dtype = "auto"
kv_cache_dtype = "fp8_e4m3"
batch_size = 128          # V46: 256
workers = 8               # V46: 16
attempts = 8              # V46: 8 (same)
turns = 128               # V46: 128 (same)
early_stop = 4            # V46: 4 (same)
temperature = 1.0         # V46: 1.0 (same)
top_logprobs = 5          # V46: 5 (same)
max_tokens_per_turn = 12288  # NEW in exp02 (V46: unlimited)
```

### Notebook generation
All experiment notebooks are generated from V46 base via cell-index patching:
```bash
python3 scripts/create_experiment_notebooks.py
```
This regenerates all 8 notebooks from `notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb`.

## 6. Immediate Next Steps

### Step A: Check if exp04 has scored
```bash
# Use Python 3.11 (3.8 has type hint issues with the scripts)
KAGGLE=/Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle

$KAGGLE competitions submissions -c ai-mathematical-olympiad-progress-prize-3
```
Look for `exp04_speed_profile` row — if `COMPLETE`, note the public score.

### Step B: Submit exp05 (after exp04 clears)
```bash
$KAGGLE competitions submit \
  -c ai-mathematical-olympiad-progress-prize-3 \
  -k r1cky7/aimo3-exp05-more-attempts \
  -f submission.parquet -v 1 \
  -m "exp05_more_attempts"
```

### Step C: Submit exp06 (after exp05 clears)
```bash
$KAGGLE competitions submit \
  -c ai-mathematical-olympiad-progress-prize-3 \
  -k r1cky7/aimo3-exp06-prompt-verify \
  -f submission.parquet -v 1 \
  -m "exp06_prompt_verify"
```

### Step D: Compare all scores and decide next direction
After exp04-exp06 are scored, update the experiment matrix and decide:
- If any single change beats 40 → combine winning changes into a new experiment
- If none beats 40 → try different approaches (see Future Ideas below)

## 7. How to Create a New Experiment

1. Add the experiment spec to `scripts/create_experiment_notebooks.py`:
   - Define a function `exp09_name(cfg: str, solver: str) -> tuple[str, str]`
   - Add an `ExperimentSpec(...)` to `SPECS_V2` list
2. Run the generator:
   ```bash
   python3 scripts/create_experiment_notebooks.py
   ```
3. Push to Kaggle:
   ```bash
   python3 scripts/kaggle_kernel_run.py \
     --metadata experiments/exp09_name/kernel-metadata.json \
     --kaggle-bin /Library/Frameworks/Python.framework/Versions/3.11/bin/kaggle \
     --download-output always
   ```
4. After kernel COMPLETE, submit to leaderboard:
   ```bash
   $KAGGLE competitions submit \
     -c ai-mathematical-olympiad-progress-prize-3 \
     -k r1cky7/aimo3-exp09-name \
     -f submission.parquet -v 1 \
     -m "exp09_name"
   ```

## 8. Operational Gotchas

| Gotcha | Details |
|--------|---------|
| **Python version** | Use Python 3.11 (`/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`). The scripts use `list[str]` type hints that fail on 3.8 |
| **One pending submission** | Kaggle allows only 1 pending competition submission at a time. Must wait for scoring to complete before submitting next |
| **2 GPU sessions max** | Kaggle limits to 2 concurrent GPU kernel sessions |
| **Code competition** | Cannot upload parquet directly (400 error). Must submit via `-k` flag pointing to a kernel |
| **Slug length** | Long Kaggle kernel slugs can cause "Notebook not found" on push. Keep slugs short |
| **model_sources case** | Must use uppercase `Transformers` in metadata: `danielhanchen/gpt-oss-120b/Transformers/default/1` |
| **Scoring runtime** | Competition submission re-runs the full kernel (up to 9 hours) — expect long waits |
| **Kaggle CLI** | Network calls from sandbox may fail with DNS errors. Use `--kaggle-bin` to point to system Python's kaggle |

## 9. Future Ideas (Not Yet Tried)

These are potential directions if exp05/exp06 don't reach 43+:

1. **Better token budget allocation**: Instead of fixed 12288 per turn, dynamically allocate based on problem difficulty (easy problems get fewer tokens)
2. **Two-pass strategy**: Fast first pass with low attempts to triage easy vs hard problems, then concentrate remaining time on hard ones
3. **Model quantization tuning**: Try different kv_cache_dtype or quantization schemes for speed vs accuracy tradeoff
4. **Prompt engineering**: Problem-type-specific prompts (geometry vs algebra vs number theory)
5. **Answer verification loop**: After getting a candidate answer, ask the model to verify it in a separate turn
6. **Ensemble with different temperatures**: Run some attempts at temp=0.7 and some at temp=1.0
7. **Early termination optimization**: Better detection of when the model has found an answer (before </think> tag)

## 10. Repository Structure

```
aimo3/
├── CLAUDE.md                          # Project instructions for Claude Code
├── kernel-metadata.json               # Root kernel config (points to V46 notebook)
├── notebooks/
│   ├── aimo-3-..._v6.ipynb           # V46 base notebook (source of truth)
│   └── aimo-3-...with-tools.ipynb    # Old development notebook (minified)
├── experiments/
│   ├── README.md
│   ├── exp01_workers_batch/           # V1: workers/batch tuning
│   ├── exp02_token_cap/               # V1: token cap (BEST: score 40)
│   ├── exp03_parser_vote/             # V1: wider parser + vote sort (score 38)
│   ├── exp04_speed_profile/           # V1: dynamic speed profiling
│   ├── exp05_more_attempts/           # V2: 16 attempts (from exp02)
│   ├── exp06_prompt_verify/           # V2: verification prompt (from exp02)
│   ├── exp07_parser_vote_from_exp02/  # V2: parser/vote isolated (from exp02)
│   └── exp08_combined_best/           # V2: all combined (from exp02)
├── scripts/
│   ├── create_experiment_notebooks.py # Generate experiment notebooks
│   ├── kaggle_kernel_run.py           # Push/run/poll Kaggle kernels
│   └── push_github.sh                # Push to GitHub
├── docs/
│   ├── EXPERIMENT_LOG.md              # Chronological history
│   ├── EXPERIMENT_TODO.md             # Task checklist
│   ├── V46_GAP_ANALYSIS.md            # V46 vs current diff analysis
│   ├── KAGGLE_KERNEL_WORKFLOW.md      # Kernel workflow guide
│   └── GIT_PUSH_WORKFLOW.md           # Git workflow guide
└── .claude/
    ├── commands/                      # Custom slash commands
    └── settings.local.json            # Tool permissions
```

## 11. Submission History

| Date | Description | Status | Public Score |
|------|------------|--------|-------------|
| 2025-12-16 | (early attempt) | COMPLETE | 0 |
| 2026-01-08 | (early attempt) | COMPLETE | 35 |
| 2026-01-28 | (early attempt) | COMPLETE | 0 |
| 2026-02-08 | V6? (V46 baseline) | COMPLETE | **38** |
| 2026-02-23 | exp02_v9_code_submit | COMPLETE | **40** |
| 2026-03-01 | exp03_parser_vote | COMPLETE | **38** |
| 2026-03-02 | exp04_speed_profile | **PENDING** | — |
