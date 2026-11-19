# Review of Pair C : the routing rule

Reviewed Files used or created by the Pair C : `TD2_groupC.md`, `atelier-routage-paire-C.py`, `simu-avant-paire-C.txt`, `simu-apres-paire-C.txt`.
Checks run: family rates recomputed from `traces-td1.csv` (last attempt per model and question), the simulator rerun, and extra cases tested.

## Insight

Solid and nearly complete. The family rates are exact. The first model of each family follows the price rule, the `none` constraint is respected, and the simulator reproduces `simu-apres-paire-C.txt` exactly. **Three fixes are required before hand-in.**

| Requirement | Status |
|---|---|
| One-page rule, one section per family | verified |
| Exact TD 1 rates with C01–C20 cells | all verified |
| First model = cheapest model correct on the family | verified |
| Checking per use, with the `none` consistency constraint | verified |
| Fallback (next model, defer, abstain) | verified |
| Simulator outputs before and after | verified |
| TD 1 cells in the `reason` of **every** decision | ✘ missing in both `abstain` |
| Analysis of the priority order in `choose` | ⚠ one invalid argument |
| Delivered in `reports/td2.md` | not yet, .md in the TD2_groupC.md |

## Required fixes

1. **Add TD 1 evidence to the `abstain` reasons.** "budget exhausted" and "unknown capability" cite no cells. Snippet to fix in `choose`:
   ```python
   if not eligible:
       reason = f"family {family} absent from C01-C20: no TD 1 evidence"
   else:
       reason = ("no eligible resource within deadline and budget; eligible on "
                 + "; ".join(evidence(r, family) for r in eligible if r["access"] == "free"))
   ```
   Then regenerate `simu-apres-paire-C.txt`.
2. **Remove the "eligibility comes before cost" reversal argument.** In `choose`, the eligibility filter runs before the `run` and `defer` branches, so a non-eligible subscription never competes with deferring. It is not a priority reversal. Replace it with a real operational condition:
   - the remaining allocation is lower than the urgent load expected before the period ends;
   - the subscription is shared with other uses;
   - overage is billed, so today's `cash == 0` becomes a real cost for the next request.

   In every case, defer only if the refill comes before `deadline_minutes` minus a safety margin.


## Recommended clarifications

- **C03, C13, C14** combine a period and products. State explicitly that F3 means "products, with or without a period" and that "Combinations" means "age combined with a period and/or products". The rates do not change (all 4/4).
- **Cohere vs Dots tie**: both have `list_price = 0.0`, and the code breaks the tie alphabetically by `id`. Say so. Also say that `0.0` means "free route, no documented paid tariff", not "a paid tariff of zero".
- **Qwen excluded from F1**: it scores 5/6 only because C20 was `not_executed` (HTTP 429), not because it made an error. The exclusion is prudent, but it must be written, since the assignment says "at least one error".
- **Correlated quorum members**: the F2 customer quorum (120B, Qwen, 20B) and the combinations 2-of-2 (20B + 120B) both pair two `gpt-oss` models. In the combinations case, the reference SQL check is therefore essential, not optional.
- **Quorum feasibility**: `choose` returns one resource and does not check that the other quorum members are available. Add one sentence: if the quorum cannot be assembled, defer or abstain.
- **Code details**:
  - the 2000/300 token envelope is unchecked (traces: prompts ≤ 666 tokens, completions median 130);
  - `allocation` is unused for the paid routes;
  - the paid Groq routes being available is a simulation assumption;
  - "reference SQL check" should read "independently written exact query" for real questions.
