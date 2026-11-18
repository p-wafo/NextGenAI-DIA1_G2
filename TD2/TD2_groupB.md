# TD2 — Pair B: shared wrong value on C02

C02 asks for the total revenue excluding VAT across all orders placed by customers who were exactly 25 on 25 September 2026. The TD1 reference is **590,320 cents**. GPT-OSS 20B (Groq) and Dots (OpenRouter) both returned **0 cents**, the only shared wrong value across the 100 final TD1 cells. The 106 stored records include six retries. The analysis keeps the last record for each model and question, as in Pair A's vote. [Original TD1 traces](../TD1/traces/traces-td1.csv) · [TD1 references](../TD1/reference-td1.csv)

| TD1 model | C02 value in cents | TD1 verdict | Fixed panel |
|---|---:|---|---|
| Groq GPT-OSS 120B | 590320 | correct | Yes |
| OpenRouter Cohere North Mini Code | 2606320 | incorrect | Yes |
| Groq Qwen 3.8 27B | 590320 | correct | Yes |
| Groq GPT-OSS 20B | 0 | incorrect | |
| OpenRouter Dots 3 Note Preview | 0 | incorrect | |

In the fixed panel with `k=2, n=3`, two votes elect 590320. With `k=3, n=5`, 590320 and 0 each get two votes and 2606320 gets one. The vote abstains. A separate panel picked after looking at the traces (20B, Dots, Cohere) would elect 0 with two votes out of three. This illustrates the effect of panel composition. The two official panels are reproduced with the team's existing vote script. [Pair A results](vote-2of3-vs-3of5.jsonl)

## Two original queries and their causes

- [M1, complete SQL from GPT-OSS 20B](sql/m1-gpt20b.sql). Its `WHERE` selects birthdays in `(2025-09-25, 2026-09-25]`, a window that corresponds to ages below one. The SQLite database contains zero customers in that window.
- [M2, complete SQL from Dots](sql/m2-dots.sql). Its birth-date predicates select only 25 September 2001, the exact 25th birthday. Its order-date predicates also restrict orders to 25 September 2026. The question asks for all orders from eligible customers. The database's last order is on 20 September. Removing the order filter alone gives 135000 cents from the single birthday match. Correcting both filters gives 590320 cents.

Both faulty SQL statements were replayed on `data/boutique.sqlite` and returned 0. Their empty sums become 0 because of `COALESCE`. The [reference query](sql/reference-c02.sql) selects birthdays in `(2000-09-25, 2001-09-25]` and includes all their orders. The lower endpoint is excluded because that customer has already turned 26. The upper endpoint is included because that customer has just turned 25. [Predicate checks](sql/diagnostic-predicates.sql) · [Separate checks for M2](sql/diagnostic-m2.sql)

## Delta on the official SQLite database

The [delta SELECT](sql/delta-c02.sql) marks each order line according to whether the reference, M1 and M2 include it. It returns per-customer differences as reference minus model, using quantity times price in integer cents.

| Customer | Order lines | Reference cents | Delta vs M1 | Delta vs M2 |
|---|---:|---:|---:|---:|
| C001 | 18 | 135000 | 135000 | 135000 |
| C002 | 6 | 25920 | 25920 | 25920 |
| C005 | 20 | 150240 | 150240 | 150240 |
| C007 | 18 | 118740 | 118740 | 118740 |
| C008 | 11 | 99090 | 99090 | 99090 |
| C009 | 9 | 61330 | 61330 | 61330 |
| **Total** | **82** | **590320** | **590320** | **590320** |

The two deltas account for all 590320 missing cents. A separate Python calculation reads the three official CSV files, computes age by comparing the birthday to the reference date and recomputes each customer's revenue and line count. All six customer totals and line counts match. [Execution evidence](c02-evidence.json)

From the repository root, run `python TD2/check-c02.py` to reproduce the SQL and CSV checks and `python vote-quorum.py --traces TD1/traces/traces-td1.csv` to reproduce the votes. These commands use the stored TD1 batch and require no new model calls. The historical fallback was unnecessary. One case on one database shows why an agreement on a number can require an independent SQL check, especially for a customer-facing figure or payout.
