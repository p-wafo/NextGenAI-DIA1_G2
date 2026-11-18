## Step 2: the wrong consensus (Pair B)

**Nature: real batch.** Full analysis: [TD2/wrong-consensus.md](../TD2/wrong-consensus.md). All figures are reproduced by [TD2/pair_b_check.py](../TD2/pair_b_check.py) ([output](../TD2/pair_b_check-output.txt)).

- **Case:** C02 (customers exactly 25 years old on 2026-09-25), the only shared wrong value in our 100 TD 1 cells. GPT-OSS 20B and Dots3-Note both return **0**; the independent reference is **590 320** cents.
- **Quorums:** the fixed 2-of-3 panel (GPT-OSS 120B, Cohere, Qwen) returns a consensus on 590 320, because 20B and Dots are not members. The 3-of-5 quorum over the five TD 1 models abstains: 0 and 590 320 tie at 2 votes.
- **Cause:** two different `WHERE` errors. GPT-OSS 20B does not subtract 25 years and selects customers aged 0. Dots keeps a single birth date and adds an order-date filter on a day with no order. Both select an empty set, and `COALESCE` returns 0.
- **Delta:** 6 customers, 82 order lines, 590 320 cents missed by each faulty query, nothing wrongly added.
- **Check that detects it:** count the population selected by the filter; a zero amount with a non-empty reference population is escalated to the reference computation. True zeros (C06, C14) pass.
- **Consequence:** agreement on 0 deserves less trust than agreement on another amount. On age questions with consequences, a quorum alone is not enough.
- **Synthetic example DEMO-VOTE**, kept separate from our counts: `>` instead of `>=` on the start bound gives [0, 0, 100], and the 2-of-3 vote returns 0 against a reference of 100.
