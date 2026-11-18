# TD 2 – Wrong consensus (Pair B)

## Part 2 – Shared wrong value on C02

### Sources
- TD 1 traces: [traces-td1.csv](../TD1/traces/traces-td1.csv) (106 rows, 100 cells, nature = real)
- TD 1 references: [reference-td1.csv](../TD1/reference-td1.csv)
- Detailed evidence (all queries, full tables, contributions): [wrong-consensus.md](wrong-consensus.md) · SQL files: [sql/](sql/) · Check script: [pair_b_check.py](pair_b_check.py) ([output](pair_b_check-output.txt))

### Rule
- Search all five TD 1 models, not only the fixed panel, for a question where at least two models return the same value with `verdict = incorrect`.
- Keep the last attempt of each model, as in Part 1.
- Declare the panel and k before reading the result, then run the group's `vote_k_sur_n`.
- Prove the cause in SQL on `data/boutique.sqlite`, read-only. The reference is used only after the vote.

### The case found

Exactly one shared wrong value exists in our 100 cells: **C02**, customers exactly 25 years old on 2026-09-25, all their orders. Reference: **590320** cents.

| Model | C02 value | Verdict | Fixed panel |
|---|---|---|---|
| `gpt-oss-120b` | 590320 | correct | yes |
| `north-mini-code` | 2606320 | incorrect | yes |
| `qwen3.8-27b` | 590320 | correct | yes |
| `gpt-oss-20b` | **0** | incorrect | no |
| `dots-3-note-preview` | **0** | incorrect | no |

### Quorum verdict

| Panel | k of n | Votes | Decision | Does 0 win? |
|---|---|---|---|---|
| Fixed panel (`gpt-oss-120b`, `north-mini-code`, `qwen3.8-27b`) | 2 of 3 | 590320: 2 · 2606320: 1 | consensus 590320 ✔ | no: 20B and Dots are not members |
| All five TD 1 models | 3 of 5 | 590320: 2 · 0: 2 · 2606320: 1 | abstain | no, but the right value does not win either |

Votes counted by hand, then checked with `vote_k_sur_n`: same decisions. A 2-of-3 panel of distinct families made of `gpt-oss-20b`, `north-mini-code` and `dots-3-note-preview` would elect 0.

### Faulty SQL clauses
The `JOIN`s are correct in both queries; the error is in the `WHERE`. The required window is birth date in ]2000-09-25 ; 2001-09-25].
- **`gpt-oss-20b`** ([query](sql/c02-faulty-gpt-oss-20b.sql)): `birth_date > '2025-09-25' AND birth_date <= '2026-09-25'`. It keeps the reference date without subtracting 25 years and selects customers aged 0. No customer is in that window (birth dates go from 1958-06-08 to 2006-08-15).
- **`dots-3-note-preview`** ([query](sql/c02-faulty-dots.sql)): a single birth date, 2001-09-25, instead of a one-year window (alone: 135000, C001 only), plus orders placed on 2026-09-25 only, which the question does not ask (alone: 0, the last order is 2026-09-20). With the correct age window, the order-day filter still gives 0.
- **Why they agree.** Two different errors, the same effect: each filter selects an empty set, and `COALESCE(SUM(...), 0)` turns it into 0.

### Delta query on `data/boutique.sqlite`
[c02-delta.sql](sql/c02-delta.sql) applies each `WHERE` clause line by line and lists the customers whose revenue differs.

| Customer | Birth date | Order lines | Reference | `gpt-oss-20b` | `dots-3-note-preview` |
|---|---|---|---|---|---|
| C005 | 2000-09-26 | 20 | 150240 | 0 | 0 |
| C007 | 2000-11-30 | 18 | 118740 | 0 | 0 |
| C009 | 2001-03-10 | 9 | 61330 | 0 | 0 |
| C008 | 2001-05-15 | 11 | 99090 | 0 | 0 |
| C002 | 2001-09-24 | 6 | 25920 | 0 | 0 |
| C001 | 2001-09-25 | 18 | 135000 | 0 | 0 |
| **Total** | | **82** | **590320** | **0** | **0** |

The six customers account for the whole gap (590320 − 0); nothing is wrongly added. C005 and C001 sit exactly on the two bounds of the window. An independent recomputation on the CSV files, without SQL, finds the same six customers, 82 lines and 590320 cents.

### Analysis
- **A consensus is not a proof.** Two unrelated errors converge on 0, the value of any empty filter. Agreement on 0 deserves less trust than agreement on another amount.
- **Check that detects it: count the population behind the amount** ([c02-population-check.sql](sql/c02-population-check.sql)). Reference: 6 customers, 82 lines. Both faulty filters: 0 and 0. A zero amount with a non-empty reference population is escalated to the reference computation. True zeros (C06, C14) pass: their population is empty too.
- **Panel choice.** The fixed 2-of-3 panel avoids this case only by its composition. The 3-of-5 quorum does not elect 0 but abstains, so the question must be escalated. A larger panel is a candidate check, not a guarantee.
- **For the routing rule (Part 3).** On age questions, a figure shown to a customer or paid out should not rely on a quorum alone: the population check or the reference computation is required.

### Mechanism illustrated: DEMO-VOTE (synthetic)
Constructed teaching material, not model outputs and not the shop database. One sale on 2026-01-01 for 100 cents; period 1 January inclusive to 2 January exclusive. `sale_date > '2026-01-01'` gives 0, `sale_date >= '2026-01-01'` gives 100. Proposals [0, 0, 100], 2 of 3: `vote_k_sur_n` elects 0 against a reference of 100.

### How to reproduce
```
python TD2/pair_b_check.py
```
The script runs offline and read-only: database fingerprint, search of the traces, votes with `vote_k_sur_n`, every SQL file of `TD2/sql`, the CSV recomputation and DEMO-VOTE.

## Limits
One database, twenty questions, one run per model. This case describes our batch, not a general error rate or a guarantee for any quorum.

## Use of AI assistance
Part of the search, the SQL files and `pair_b_check.py` were prepared with an AI assistant. Pair B (Pierre-Olivier WAFO BAKAM, Oryssa Stella TALATALA and Hugo HOUPPE) ran every query and compared each value with the reference and with the CSV recomputation. Pierre-Olivier and Oryssa worked together on the same tasks; Hugo reproduced all figures independently with his own queries and script.
