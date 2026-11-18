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

