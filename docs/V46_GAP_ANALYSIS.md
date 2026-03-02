# V46 Gap Analysis (Fact-Only)

Updated: 2026-02-23 23:10 JST

## Scope
- Target claim: "`V46` was good, identify exact differences."
- Method: compare Kaggle pulled artifacts, local notebooks, experiment notebooks, kernel logs, and submission records.
- Policy: no assumptions; only confirmed outputs/logs.

## 1) V46 Artifact Identity Check

### Pulled artifacts
- `/private/tmp/aimo3_v46_check/aimo-3-gpt-oss-120b-with-tools.ipynb`
- `/private/tmp/aimo3_latest_check/aimo-3-gpt-oss-120b-with-tools.ipynb`

### File hash (SHA256)
- V46 notebook: `a245512c91a0897727dbadfa2de0b249beb8ff9b6cafd659409dcb7372e5f122`
- Latest notebook: `a245512c91a0897727dbadfa2de0b249beb8ff9b6cafd659409dcb7372e5f122`
- Result: identical bytes.

### Code-only hash (all code cells concatenated)
- V46 pulled notebook: `ff4adcc5fd0bb32cbd651d5807a067efec5b94aff5bf039c6e69b3bafa2f1485`
- Local `notebooks/aimo-3-gpt-oss-120b-with-tools _v6.ipynb`: same hash (`ff4a...`)
- Local `notebooks/aimo-3-gpt-oss-120b-with-tools.ipynb`: different hash (`9a48fef74e5b0615257a00a92a222ac5b757ec27d5c5e0656e0bc787d90de615`)

Confirmed:
- Current Kaggle pull (`latest`) and `V46` pull are identical.
- The code currently deployed from root metadata corresponds to local `_v6` notebook, not `notebooks/aimo-3-gpt-oss-120b-with-tools.ipynb`.

## 2) V46 Runtime Status and Failure Cause
- Command result: `kaggle kernels status r1cky7/aimo-3-gpt-oss-120b-with-tools/46`
- Status: `KernelWorkerStatus.ERROR`
- Pulled log: `/private/tmp/aimo3_v46_output/aimo-3-gpt-oss-120b-with-tools.log`
- Confirmed failure:
  - `tar (child): /kaggle/input/aimo-3-utils/wheels.tar.gz: Cannot open: No such file or directory`
  - `CalledProcessError` in `set_env(... input_archive='/kaggle/input/aimo-3-utils/wheels.tar.gz' ...)`

Conclusion:
- The checked `V46` run failed during setup due to fixed wheels path.

## 3) Submission Evidence Around Score 38
- Submission list snapshot:
  - `2026-02-08 12:44:20.397000`, description `V6?`, status `COMPLETE`, publicScore `38`
  - `2026-02-23 13:59:08.660000`, description `exp02_v9_code_submit`, status `PENDING`

Confirmed:
- Most recent completed public score remains 38 from `2026-02-08`.
- New exp submission is still pending as of this update.

## 4) Core Code Differences

## V46 (_v6) vs local current base notebook (`notebooks/aimo-3-gpt-oss-120b-with-tools.ipynb`)
- Model/runtime parameters differ:
  - `model_path`: V46=`/kaggle/input/gpt-oss-120b/transformers/default/1`, base=`/kaggle/input/gpt-oss-120b-eagle3-throughput`
  - `kv_cache_dtype`: V46=`fp8_e4m3`, base=`fp16`
  - `dtype`: V46=`auto`, base=`float16`
  - `top_logprobs`: V46=`5`, base=`0`
  - `batch_size`: V46=`256`, base=`64`
  - `attempts`: V46=`8`, base=`4`
  - `turns`: V46=`128`, base=`64`
  - `early_stop`: V46=`4`, base=`3`
  - `temperature`: V46=`1.0`, base=`0.7`
- Control flow differs:
  - V46 hard-enforces H100 (`_assert_h100_environment`), base has soft disable fallback (`_should_disable_vllm`).
  - V46 eagerly constructs solver in notebook cell; base uses lazy init with lock.
  - Base adds dynamic speed profile (`_select_speed_profile`); V46 uses fixed attempts/turns.
  - Base enforces strict archive existence check; V46 original setup does not precheck and fails at tar call.

## V46 (_v6) vs experiments
- Shared reliability patches in all exp notebooks:
  - `resolve_input_archive()`
  - `CFG.resolve_model_path()`
  - `resolve_test_csv_path()`
- Resource pressure reduction in generated experiments:
  - `batch_size` changed `256 -> 128`
  - `workers` changed `16 -> 8`
- Experiment-specific deltas:
  - `exp02`: `max_tokens_per_turn = 12288`
  - `exp03`: broader answer parser + vote-priority sort
  - `exp04`: dynamic speed profile (attempts/turns/early-stop by remaining time)

## 5) What Is Confirmed vs Not Confirmed

Confirmed:
- `V46` pull == `latest` pull.
- `V46` code == local `_v6` notebook code.
- `V46` checked run failed due to missing wheels archive path.
- Current best completed public score is still 38 (`2026-02-08`).

Not yet confirmed:
- Which exact code delta from V46-style logic changes leaderboard score relative to 38 (no completed post-38 score yet; pending submission in queue).

## 6) Next Isolation Plan (TODO)
- Run control notebook: V46 logic + only reliability fixes (no scoring logic changes).
- Run single-factor ablations from control:
  - batch/workers reduction only
  - token cap only
  - parser/vote change only
  - speed-profile change only
- Submit each via code-submission path and compare public score against 38.
