# Review of Pair B: the wrong consensus

Reviewers: Pair A · Internal cross-review
Files read: `TD2_groupB.md`, `pair_b_check.py`, `pair_b_check-output.txt`
Checks run: `pair_b_check.py` rerun on a fresh clone, shared wrong values searched again in `traces-td1.csv`, votes compared with Pair A's `vote_k_sur_n` and `vote-quorum.py`.

## Insight

Complete and reproducible. The rerun of `pair_b_check.py` gives an output **identical** to `pair_b_check-output.txt`. C02 = 0 is the only shared wrong value, whether we keep every row or only the last attempt per model. The quorum verdicts match Pair A's 20-question table. **No blocking fix; four improvements suggested.**

| Requirement (Step 2) | Status |
|---|---|
| Search across the five TD 1 models, not only the fixed panel | verified |
| Identification: question, models, shared value, reference (590320, `reference-td1.csv`) | verified |
| 2-of-3 and 3-of-5 verdicts, hand count checked with `vote_k_sur_n` | verified (590320 / abstain) |
| Both faulty SQL queries, root cause in the `WHERE` clause | verified |
| Delta query on `data/boutique.sqlite` explaining the whole gap | verified (6 customers, 82 lines, 590320) |
| Independent checking method | verified (CSV recomputation, population check) |
| DEMO-VOTE kept separate and labelled synthetic | verified |
| Delivered in `reports/td2.md` | not yet, still in `TD2/TD2_groupB.md` |

## What is convincing

- **Root cause.** Two different `WHERE` errors give the same 0: GPT-OSS 20B forgets to subtract 25 years (window ]2025-09-25 ; 2026-09-25]), Dots keeps one birth date and adds an order-day filter. Both select an empty set, and `COALESCE(SUM(...), 0)` turns it into 0.
- **Clause isolation.** Running each Dots condition alone (135000, then 0, then 0 with the correct window) proves which clause empties the result.
- **Three independent confirmations** of 590320: reference SQL, delta per customer, recomputation in Python without SQL.
- **Population check.** It separates the false 0 of C02 (6 customers expected) from the true 0 of C06 and C14 (0 customers). It is a practical check for the routing rule.

## Suggested improvements

1. **3-of-5 panel built from the rows found** (`pair_b_check.py`, section 2). The five proposals come from `last.items()`, so a model with no row on a question would leave n instead of staying in n without a vote. No effect on C02 (five rows), but a fixed list of five models, as in `vote-quorum.py`, would match the contract.
2. **Retries in the search** (section 1). The search reads every row, while the rule says "last attempt". The result is the same here (checked), but filtering on the last attempt would match the stated rule.
3. **DEMO-VOTE labels.** The synthetic proposals reuse `vote_module.PANEL`, so the output shows real model names (`gpt-oss-120b`, `north-mini-code`) on invented values. Neutral names (`model-1`, `model-2`, `model-3`) would avoid confusion with real results.
4. **Path assumption.** `ROOT = parents[1]` works only while the script stays in `TD2/`. If it moves into a `Pair B/` folder, it will break.

## Questions for Pair B

- Does the population check run only when the amount is 0, or also on any amount? Cohere's 2606320 on C02 is wrong but non-zero: would the check catch it?
- With a 2-of-3 panel of GPT-OSS 20B, Cohere and Dots, 0 wins. Should the routing rule pick panel members from models correct on the family, rather than only from distinct providers?

## Link with Part 1 (Pair A)

- C02 explains the only "consensus -> abstention" change in our 2-of-3 vs 3-of-5 table: the two extra models add the shared wrong value, so 590320 and 0 tie at 2 votes.
- With our panel, no wrong consensus appears on the 20 questions. Pair B shows this comes from the panel composition, not from the vote itself.
