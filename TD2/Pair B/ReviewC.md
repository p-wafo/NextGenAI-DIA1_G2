# Code review — Pair C (routing rule and simulator)

Reviewer: Pair B (Pierre-Olivier WAFO BAKAM, Oryssa Stella TALATALA, Hugo HOUPPE) · Internal cross-review, TD 2, 18 November 2026
Commit reviewed: `d434217` (main, 16:44), after the move of Pair C's files to `TD2/Pair C/`

## Scope

| File | Role |
|---|---|
| `TD2/Pair C/TD2_groupC.md` | one-page routing rule and analysis of `choose` |
| `TD2/Pair C/atelier-routage-paire-C.py` | simulator adapted to the rule |
| `TD2/Pair C/simu-avant-paire-C.txt`, `TD2/Pair C/simu-apres-paire-C.txt` | outputs before and after adaptation |
| `atelier-routage.py` | supplied simulator (reference for "before") |

Method: recounted every TD 1 rate per family from `TD1/traces/traces-td1.csv`, read `choose` branch by branch, ran both simulators and compared their output with the stored files.

## Verdict

The rule is **correct and well justified**: all accuracy rates per family match the traces, the "none" check respects the consistency constraint, and every simulator decision carries a reason with the TD 1 cells. Both stored outputs match a fresh run. The issues below are about **links broken by the move to `TD2/Pair C/`**, **coverage of the simulator** and **two points of the analysis**, not about errors in the rates.

## What works (verified)

- **Rates per family**, all recounted from the traces: F1 (120B, 20B, Cohere, Dots 6/6; Qwen 5/6, C20 HTTP 429), F2 (120B 4/4, Qwen 4/4, 20B 3/4, Cohere 1/4, Dots 0/4), F2b (C10), F3 (4/4 for all), combinations (120B and 20B 5/5, Cohere and Dots 2/5, Qwen 0/5).
- **Eligibility** in the code (`COHERE`, `DOTS`, `OSS_20B`, `OSS_120B`, `QWEN`) matches the "100 % on the family" rule, including Qwen excluded from F1 because of the non-executed C20.
- **Consistency constraint**: "none" is only used for the internal dashboard with a model at 100 % on the family; customer figures and payouts require a quorum or a deterministic check.
- **Reasons**: every `run` and `defer` decision cites the family, its cells and the model's ratio, e.g. `TD 1 F1 period (C01, C04, C05, C06, C07, C20): cohere-north-mini-code-free 6/6`.
- **Outputs**: `simu-avant` and `simu-apres` match a fresh run of `atelier-routage.py` and `TD2/Pair C/atelier-routage-paire-C.py`, and are now readable UTF-8. The script still runs from its new folder (no file-relative import).
- **Branches of `choose`**: run (free), defer (Groq Free exhausted, refill before the deadline), run (paid, urgent), abstain (budget 0), abstain (unknown family) are all exercised.

## Issues

### 0. Should fix — links and commands broken by the move to `TD2/Pair C/`

The move (commit `94bdc5a`) did not update the paths that point to these files:

| File | Broken reference | Correct reference |
|---|---|---|
| `TD2/Pair C/TD2_groupC.md` (Sources) | `../TD1/results/pivot-view.md`, `../TD1/results/model-question-comparison-en.csv`, `../TD1/results/five-model-summary-en.csv` | `../../TD1/results/...` (one level deeper) |
| `TD2/TD2.md` (Simulator outputs, l. 258–259) | `simu-avant-paire-C.txt`, `simu-apres-paire-C.txt`, `atelier-routage-paire-C.py` | `Pair%20C/simu-avant-paire-C.txt`, etc. (`%20` for the space in a Markdown link) |
| `README.md` (Replay the TD 2 work, l. 116) | `python TD2/atelier-routage-paire-C.py` | `python "TD2/Pair C/atelier-routage-paire-C.py"` |
| `README.md` (layout, l. 52) | `atelier-routage-paire-C.py, simu-*.txt` directly under `TD2/` | under `TD2/Pair C/` |

### 1. Should fix — the customer-facing rule is never exercised

`TD2_groupC.md` defines three uses, but the seven scenarios only cover `internal` (six) and `payout` (one). The `customer` branch of `checks_for` (l. 79–85), including the special case for combinations, never appears in `simu-apres`. Adding two scenarios would show it:

```python
("customer age", {**base, "family": "F2", "use": "customer"}, RESOURCES),
("customer combination", {**base, "family": "COMB", "use": "customer"}, RESOURCES),
```

### 2. Should fix — misleading `checks` on abstentions

When the simulator abstains, the `checks` field still says `none (first model 100 % correct on the family in TD 1)`:
- `budget exhausted`: no model runs;
- `unknown capability` (F4): no model is 100 % on F4, and l. 96 falls back to `CHECKS[use]`.

The text claims something that is false for these decisions. Suggested fix: return `"checks": "n/a (no model called)"` in the abstain branch.

### 3. Should fix (from Pair B's analysis) — a quorum alone is weak on age questions

For F2 customer figures the rule requires a 2-of-3 quorum among 120B, Qwen and 20B. On C02, `gpt-oss-20b` and `dots-3-note-preview` returned the **same wrong value 0** ([TD2_groupB.md](../TD2_groupB.md)): two models can fail together, and 0 is what any empty filter returns. Suggested addition for F2, F2b and combinations shown to a customer: when the elected amount is 0, run the population check ([c02-population-check.sql](../sql/c02-population-check.sql)) and escalate if the reference population is not empty.

### 4. Remark — the combinations check relies on one model family

For combinations shown to a customer, the rule requires the agreement of `gpt-oss-20b` and `gpt-oss-120b`. Both are GPT-OSS models, so their agreement is weaker evidence than two distinct families. The rule compensates with a reference SQL check, which is the right call; the write-up could say why.

### 5. Remark — second reversal condition in "Priority order in `choose`"

`TD2_groupC.md` l. 55 says the priority should also be reversed "when the free model is the one that was 100 % correct on the family and the subscription model was not, since eligibility comes before cost". In `choose`, eligibility is filtered **first** (`eligible = [...]`): a model that is not eligible for the family is never in `included`, so this situation cannot occur. The first condition (scarce or shared subscription allocation, request that can wait, refill before `deadline_minutes` with a margin) is the real answer; the second sentence could be removed.

### 6. Minor — token envelope three times larger than measured

`ENVELOPE_IN = 2000` and `ENVELOPE_OUT = 300` (l. 19–20) are flagged as "to check against the traces". Measured in `traces-td1.csv`:

| Model | Input tokens (median) | Output tokens (median / max) |
|---|---:|---:|
| gpt-oss-120b | 638 | 183 / 496 |
| gpt-oss-20b | 638 | 194 / 617 |
| qwen3.8-27b | 630 | 120 / 251 |

The input envelope overestimates the cost by about 3×; the output envelope is below the observed maximum. The ranking of the paid routes does not change, but the cash values in `simu-apres` are not the measured cost. Either use ~650 / ~200 (median) or ~700 / ~650 (cautious), and cite the source.

### 7. Minor — tie between the two free routes

Cohere and Dots both have `list_price = 0.0`; `min(..., key=(list_price, id))` then picks Cohere because of alphabetical order. The write-up says ties are broken by the documented paid price, but neither model has one. State the actual rule (alphabetical, or another documented criterion).


## Assignment checklist

| Expected (Step 3) | Status |
|---|---|
| Exact TD 1 rate per family, citing the cells | ✔ |
| First model = cheapest among those correct on the family | ✔ |
| Checking per use (internal, customer, payout) with the consistency constraint | ✔ in the rule; customer use not exercised in the simulator (issue 1) |
| Course of action if unavailable (next model, defer, abstain) | ✔ |
| `RESOURCES` and `choose` adapted, TD 1 cells in every reason | ✔ |
| Simulator outputs before and after | ✔ files present; links from `TD2.md` broken by the move (issue 0) |
| Analysis of the priority between included capacity and deferral | ✔ first condition correct; second condition does not apply (issue 5) |

## Questions for the cross-review

1. Why is Cohere called first on F1 but GPT-OSS 120B on F2?
2. In the supplied `choose`, why is an available subscription (cash 0, allocation > 0) chosen before deferring to an exhausted free route?
3. In which situation would you defer instead, and what must be checked at wake-up?
