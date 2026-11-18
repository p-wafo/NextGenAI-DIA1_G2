# TD 2 – Vote and route

## Part 1 – k-of-n vote

### Rule
- Panel: n = 3 models from three distinct families: `groq:openai/gpt-oss-120b`, `openrouter:cohere/north-mini-code:free`, `groq:qwen/qwen3.8-27b`.
- k = 2, fixed before looking at the answers (strict majority: n//2 < k <= n).
- Only executed proposals carrying a value vote; an error (429, invalid SQL, refusal) stays in n but casts no vote.
- One model = one vote; a duplicate panel member is rejected.
- If no value reaches k, the vote abstains: it never invents a value.
- The reference is compared after the decision; the vote never sees it.

### Why k = 2 of 3
- k = 1 accepts any single answer: no protection against an isolated error.
- k = 3 requires unanimity: one unavailable model (429, timeout) blocks every decision.
- k = 2 is the smallest strict majority: two different values can never both reach it.

### Synthetic checks (`python atelier-vote.py`)

| Example | Values | Consensus | Value | Matches reference |
|---|---|---|---|---|
| agreement | 100, 100, 120 | true | 100 | true |
| disagreement | 100, 110, 120 | false | – | – |
| unavailable | 100, –, – | false | – | – |
| wrong consensus | 0, 0, 100 | true | 0 | **false** |

The last example shows the limit of the vote: two models agreeing on the same wrong value win the vote.

### Results on the TD 1 traces (`TD1/traces/traces-td1.csv`, nature = real)

| Case | Consensus | Value (cents) | Votes | Reference | Matches |
|---|---|---|---|---|---|
| C01 | true | 792800 | 3 | 792800 | true |
| C02 | true | 590320 | 2 | 590320 | true |
| C03 | true | 936350 | 3 | 936350 | true |
| C04 | true | 2826250 | 3 | 2826250 | true |
| C05 | true | 38480 | 3 | 38480 | true |
| C06 | true | 0 | 3 | 0 | true |
| C07 | true | 13970 | 3 | 13970 | true |
| C08 | true | 605580 | 3 | 605580 | true |
| C09 | true | 487980 | 2 | 487980 | true |
| C10 | true | 558980 | 2 | 558980 | true |
| C11 | true | 446690 | 2 | 446690 | true |
| C12 | true | 1666490 | 3 | 1666490 | true |
| C13 | true | 107740 | 3 | 107740 | true |
| C14 | true | 0 | 3 | 0 | true |
| C15 | **false** | – | 1 | 168680 | – |
| C16 | true | 376740 | 2 | 376740 | true |
| C17 | **false** | – | 1 | 258180 | – |
| C18 | true | 62480 | 2 | 62480 | true |
| C19 | **false** | – | 1 | 1990 | – |
| C20 | true | 1106090 | 2 | 1106090 | true |

| Indicator | Value |
|---|---|
| Coverage = consensus / 20 | 17 / 20 = **85 %** |
| Accuracy = correct consensus / consensus | 17 / 17 = **100 %** |
| Unanimous decisions (3/3) | 10 |
| Majority decisions (2/3) | 7 |
| Abstentions | 3 (C15, C17, C19) |
| Wrong consensus | **0** |

### Analysis
- **The vote absorbs isolated errors.** In 7 cases one model was wrong or failed and the two others agreed on the reference: `north-mini-code` gave a wrong value on C02, C10, C11 and invalid SQL on C09; `qwen3.8-27b` gave a wrong value on C16 and did not execute on C18 and C20. Asking that single model would have returned a wrong figure or nothing; the vote returns the reference.
- **One model is right everywhere, but we cannot know it in advance.** `gpt-oss-120b` matches the reference on 20/20 questions. The vote does not use this knowledge: it is only visible after comparing with the reference, which the vote never sees.
- **The vote abstains rather than guessing.** On C15, C17 and C19 the three models return three different values (best value: 1 vote), so no value reaches k = 2. `gpt-oss-120b` was right on all three, but `north-mini-code` and `qwen3.8-27b` were both wrong, each with a different value (e.g. C15: 168680 / 314020 / 0). These are the questions that combine several filters (period + age 25 for C15; period + products + age 25 for C17 and C19). Without the reference, nothing tells which of the three values is right, so returning nothing is safer than returning a wrong revenue figure.
- **Cost of the rule.** 100 % accuracy is paid with 15 % of unanswered questions, including 3 questions where one model actually had the right answer. k = 3 (unanimity) would keep only the 10 unanimous cases (coverage 50 %); k = 1 is not a strict majority and is rejected by the rule.
- **Limit.** No wrong consensus appears with this 3-model panel: when the two weaker models are both wrong (C15, C17, C19), they disagree with each other. Across the five TD 1 models, however, `gpt-oss-20b` and `dots-3-note-preview` share the wrong value 0 on C02 (see below and Part 2). The synthetic example shows the risk remains: two models making the same mistake (same date boundary, same age convention) would win the vote. The vote reduces independent errors, not shared ones: see Part 2.

### 2-of-3 panel vs 3-of-5 quorum (all five TD 1 models)

- 2-of-3: fixed panel `gpt-oss-120b`, `north-mini-code`, `qwen3.8-27b`, k = 2.
- 3-of-5: the same three + `groq:openai/gpt-oss-20b` + `openrouter:dots-studio/dots-3-note-preview:free`, k = 3 (strict majority of 5).
- Same rule for both: last attempt per model, an error keeps its place in n without a vote. Both decisions are computed by our `vote_k_sur_n` (`vote-quorum.py`).

| Case | Reference | 2-of-3 decision | Votes | 3-of-5 decision | Votes | Change |
|---|---|---|---|---|---|---|
| C01 | 792800 | 792800 ✔ | 3 | 792800 ✔ | 5 | margin only |
| C02 | 590320 | 590320 ✔ | 2 | **abstain** | 2 | **consensus → abstention** |
| C03 | 936350 | 936350 ✔ | 3 | 936350 ✔ | 5 | margin only |
| C04 | 2826250 | 2826250 ✔ | 3 | 2826250 ✔ | 5 | margin only |
| C05 | 38480 | 38480 ✔ | 3 | 38480 ✔ | 5 | margin only |
| C06 | 0 | 0 ✔ | 3 | 0 ✔ | 5 | margin only |
| C07 | 13970 | 13970 ✔ | 3 | 13970 ✔ | 5 | margin only |
| C08 | 605580 | 605580 ✔ | 3 | 605580 ✔ | 4 | margin only |
| C09 | 487980 | 487980 ✔ | 2 | 487980 ✔ | 3 | margin only |
| C10 | 558980 | 558980 ✔ | 2 | 558980 ✔ | 3 | margin only |
| C11 | 446690 | 446690 ✔ | 2 | 446690 ✔ | 3 | margin only |
| C12 | 1666490 | 1666490 ✔ | 3 | 1666490 ✔ | 5 | margin only |
| C13 | 107740 | 107740 ✔ | 3 | 107740 ✔ | 5 | margin only |
| C14 | 0 | 0 ✔ | 3 | 0 ✔ | 5 | margin only |
| C15 | 168680 | abstain | 1 | abstain | 2 | none (still below k) |
| C16 | 376740 | 376740 ✔ | 2 | 376740 ✔ | 3 | margin only |
| C17 | 258180 | abstain | 1 | abstain | 2 | none (still below k) |
| C18 | 62480 | 62480 ✔ | 2 | 62480 ✔ | 4 | margin only |
| C19 | 1990 | abstain | 1 | **1990 ✔** | 3 | **abstention → consensus** |
| C20 | 1106090 | 1106090 ✔ | 2 | 1106090 ✔ | 4 | margin only |

| Indicator | 2-of-3 | 3-of-5 |
|---|---|---|
| Coverage | 17 / 20 = 85 % | 17 / 20 = 85 % |
| Accuracy | 17 / 17 = 100 % | 17 / 17 = 100 % |
| Abstentions | C15, C17, C19 | C02, C15, C17 |
| Wrong consensus | 0 | 0 |

**Explanation of every question where the decision changes** (values and verdicts from `traces-td1.csv`):
- **C02 – consensus becomes abstention.** 2-of-3: `gpt-oss-120b` = 590320 (correct), `qwen3.8-27b` = 590320 (correct), `north-mini-code` = 2606320 (incorrect) → 590320 with 2 votes. 3-of-5 adds `gpt-oss-20b` = 0 (incorrect) and `dots-3-note-preview` = 0 (incorrect): the right value and the shared wrong value 0 both have 2 votes, neither reaches k = 3, so the quorum abstains. The quorum did not let the wrong value win, but it lost a correct answer. This is the shared wrong value analysed in Part 2.
- **C19 – abstention becomes consensus.** 2-of-3: `gpt-oss-120b` = 1990 (correct), `north-mini-code` = 71640 (incorrect), `qwen3.8-27b` = 83580 (incorrect) → three different values, 1 vote max. 3-of-5 adds `gpt-oss-20b` = 1990 (correct) and `dots-3-note-preview` = 1990 (correct) → 1990 with 3 votes, which matches the reference.
- **Margin only, because of an HTTP 429 or invalid SQL:**
  - C18 and C20: `qwen3.8-27b` is `not_executed` (HTTP 429). It stays in n without a vote: 2-of-3 decides with only 2 votes out of 3 (no margin left); 3-of-5 decides with 4 votes out of 5.
  - C09: `north-mini-code` returns `sql_invalid`; C11: `dots-3-note-preview` returns `sql_rejected`. Both stay in n without a vote; the decision is unchanged (2 → 3 votes).
- **C15 and C17 – no change.** `gpt-oss-120b` and `gpt-oss-20b` agree on the reference (168680, 258180), but 2 votes stay below k = 3; the three other models give three different wrong values.

**Finding.** On these traces the two quorums have the same coverage (85 %) and the same accuracy (100 %), but abstain on different questions. 3-of-5 recovers C19 thanks to two extra correct models, and loses C02 because two extra models share the same wrong value. Adding models only helps if their errors are independent. Twenty questions support this observation for this batch, not a general error rate.

### How to reproduce
```
python atelier-vote.py
foreach ($i in 1..20) { $c = "C{0:D2}" -f $i; python atelier-vote.py --traces TD1/traces/traces-td1.csv --case $c | Out-File -Append -Encoding utf8 TD2/vote-td2.jsonl }
python vote-quorum.py --traces TD1/traces/traces-td1.csv | Out-File -Encoding utf8 TD2/vote-2of3-vs-3of5.jsonl
```

## Part 2 - The wrong consensus (Pair B)

On C02, GPT-OSS 20B and Dots both returned 0 cents against a reference of 590,320 cents. The fixed 2-of-3 panel returns the reference. The 3-of-5 quorum abstains.

See the [full analysis and SQL queries](wrong-consensus.md), the [reproduction script](pair_b_check.py), and its [recorded output](pair_b_check-output.txt).


# TD 2. Routing rule (Pair C)

## Sources
- TD 1 results: [pivot view](../TD1/results/pivot-view.md), [comparison](../TD1/results/model-question-comparison-en.csv), [summary](../TD1/results/five-model-summary-en.csv)


## Price order used
All tested routes were free. Ties are broken by the documented paid price of the same model.
Cohere :free and Dots :free (OpenRouter, no paid route) < GPT-OSS 20B (0.075 / 0.30) < GPT-OSS 120B (0.15 / 0.60) < Qwen (0.80 / 4.00), in USD per million input / output tokens.

## Rule by family

### F1 period (C01, C04, C05, C06, C07, C20)
- TD 1 rate. 120B 6/6, 20B 6/6, Cohere 6/6, Qwen 5/6 (C20 not executed, HTTP 429), Dots 6/6.
- First model. Cohere :free.
- Checking. Internal dashboard, none (Cohere 6/6). Customer figure, 2-of-3 quorum (Cohere, Dots, 20B). Amount paid out, reference SQL check and human review.
- If unavailable. Dots, then 20B. Defer if the request can wait.

### F2 completed age at a date (C02, C08, C09, C11)
- TD 1 rate. 120B 4/4, 20B 3/4 (C02 wrong), Cohere 1/4, Qwen 4/4, Dots 0/4.
- First model. GPT-OSS 120B.
- Checking. Internal dashboard, none (120B 4/4). Customer figure, 2-of-3 quorum (120B, Qwen, 20B). Amount paid out, reference SQL check and human review.
- If unavailable. Qwen. If both are unavailable, defer if possible, otherwise abstain. Cohere and Dots are excluded.

### F2b age at the order (C10)
- TD 1 rate. 120B 1/1, 20B 1/1, Cohere 0/1, Qwen 1/1, Dots 0/1.
- First model. GPT-OSS 20B.
- Checking. Only one cell supports this family, so we require a 2-of-3 quorum (20B, 120B, Qwen) even for the internal dashboard. Amount paid out, reference SQL check and human review.
- If unavailable. 120B, then Qwen. Cohere and Dots are excluded.

### F3 product list (C03, C12, C13, C14)
- TD 1 rate. 4/4 for all five models.
- First model. Cohere :free.
- Checking. Internal dashboard, none. Customer figure, 2-of-3 quorum (Cohere, Dots, 20B). Amount paid out, reference SQL check and human review.
- If unavailable. Dots, then 20B.

### Combinations (C15 to C19)
- TD 1 rate. 120B 5/5, 20B 5/5, Cohere 2/5, Qwen 0/5 (C18 not executed), Dots 2/5.
- First model. GPT-OSS 20B.
- Checking. Internal dashboard, none (20B 5/5). Customer figure, 2-of-3 is not possible with only two eligible models, so we require agreement of 20B and 120B plus a reference SQL check. Amount paid out, reference SQL check and human review.
- If unavailable. 120B. If both are unavailable, defer if possible, otherwise abstain.

## Limits
Twenty questions on one dataset support a batch-specific hypothesis. They do not give a general error rate, a permanent ranking or a quorum error guarantee.

## Priority order in 'choose'

### Why an available subscription goes before deferring
In the supplied 'choose', the first branch keeps every eligible resource that is available with 'cash == 0'. A subscription with remaining allocation is in that list. An exhausted free resource is not, because it is unavailable. The 'defer' branch is only reached when that first list is empty.

So the function answers now with capacity that is already paid rather than wait. Both options cost no new cash. Running now gives the answer immediately and avoids two risks of waiting, the refill may come late, and reaching the reset time does not prove that capacity is back, so availability must be checked again at wake-up.

### When this priority should be reversed
When the subscription allocation is scarce or shared, using it on a request that can wait has a cost. It may be missing later for an urgent or high-impact request that cannot wait for a free refill. In that case, a request that can wait and whose free refill arrives before 'deadline_minutes', with a safety margin, should be deferred, and the subscription kept for requests that cannot wait.

The order should also be reversed when the free model is the one that was 100 % correct on the family in TD 1 and the subscription model was not, since eligibility comes before cost.

## Simulator outputs
- Before adaptation: [simu-avant-paire-C.txt](simu-avant-paire-C.txt)
- After adaptation: [simu-apres-paire-C.txt](simu-apres-paire-C.txt), produced by [atelier-routage-paire-C.py](atelier-routage-paire-C.py)

## Use of AI assistance
The adapted simulator and a first draft of this page were partially written with an AI assistant, then I checked against the TD 1 pivot view and run locally.

