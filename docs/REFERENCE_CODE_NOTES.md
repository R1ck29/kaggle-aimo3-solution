# Reference Code Notes: AIMO2 Fast-Math-R1

Scope
- This memo summarizes lessons applicable to AIMO3 from the AIMO2 Fast-Math-R1 solution materials.
- Primary sources: the Fast-Math-R1 repo summary and linked solution slide deck, plus a top AIMO2 solution writeup for inference strategy parallels.

What we can directly reuse in AIMO3

1) Two-stage training recipe (accuracy then efficiency)
- SFT on difficult math data improves accuracy but tends to increase output length.
- A second RL stage (GRPO in Fast-Math) is used specifically to reduce token usage while retaining accuracy.
- This implies: treat output length as a first-class objective; even small accuracy gains can be negated if the token budget is exceeded.
Sources: Fast-Math-R1 repo summary and paper link. citeturn2view0

2) Token-budget-aware inference is critical
- AIMO2 results show large accuracy drop-offs when token budgets are reduced (e.g., 8k vs 16k); the solution emphasizes efficiency under budget constraints.
- Therefore, AIMO3 inference must be budget-aware: dynamic scheduling of max tokens and number of samples based on remaining time and per-problem difficulty.
Sources: Fast-Math slide deck and Fast-Math repo summary. citeturn0search1turn2view0

3) Question-level early stopping with self-consistency
- Use self-consistency (multiple samples per question) and stop early when a majority consensus emerges (e.g., 5/7 agree).
- This avoids wasting time on long tails of difficult samples when easy consensus has already formed.
Source: AIMO2 2nd-place solution summary. citeturn1search0

4) Speed profile / dynamic hyperparameter adjustment
- Dynamically reduce sampling count and max reasoning length when average time per remaining question drops below a threshold.
- Example policy from AIMO2: switch to “fastest” mode when remaining time per question < 5 minutes, cutting samples and max time.
- This maps directly to our AIMO3 speed profiling already added in the notebook.
Source: AIMO2 2nd-place solution summary. citeturn1search0

5) Early termination at reasoning boundary tokens
- For R1-style models, the answer often appears before the closing </think> tag; early stopping at that boundary can reduce wasted tokens.
- Combine with answer extraction to reduce tail generation.
Source: Fast-Math slide deck. citeturn0search1

6) Efficiency via inference engine + quantization + KV cache
- AIMO2 top solutions emphasize inference stack efficiency: vLLM, weight quantization, and KV cache quantization.
- Practical takeaway for AIMO3: treat the serving stack as part of the model; tune quantization and KV cache to maximize batch/throughput without unacceptable quality loss.
Source: AIMO2 2nd-place solution summary. citeturn1search0

Caveats / follow-up
- I could not fetch the full README contents from the Fast-Math-R1 repo due to GitHub page load errors in this environment; we relied on the repo summary + slide deck + related solution summary.
- If you can provide the README or a local clone of the repo, I can expand this memo with concrete implementation details (exact scheduler code, config values, and scripts).

Actionable checklist for our AIMO3 pipeline
- Add / tune a speed profile module that adapts attempts, max tokens, and early-stop threshold to remaining time.
- Add question-level early stop with majority consensus threshold.
- Add “stop at </think>” parsing for faster answer extraction.
- Treat quantization + KV cache as first-order knobs; measure accuracy vs throughput trade-offs on reference problems.
