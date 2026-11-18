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
- **Limit.** No wrong consensus appears on these 20 traces with this panel: when the two weaker models are both wrong (C15, C17, C19), they disagree with each other. The synthetic example shows the risk remains: two models making the same mistake (same date boundary, same age convention) would win the vote. The vote reduces independent errors, not shared ones: see Part 2.

### How to reproduce
```
python atelier-vote.py
foreach ($i in 1..20) { $c = "C{0:D2}" -f $i; python atelier-vote.py --traces TD1/traces/traces-td1.csv --case $c | Out-File -Append -Encoding utf8 TD2/vote-td2.jsonl }
```