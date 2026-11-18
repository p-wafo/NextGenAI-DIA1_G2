# Code review — Pair A (k-of-n vote)

Reviewer: Pair B (Pierre-Olivier WAFO BAKAM, Oryssa Stella TALATALA, Hugo HOUPPE) · Internal cross-review, TD 2, 18 November 2026
Commit reviewed: `d434217` (main, 16:44)

## Scope

| File | Role |
|---|---|
| `skeleton-multi-llm-en.py`, `Orchestrateur.vote_k_sur_n` (l. 603–668) | the vote |
| `TD2/Pair A/vote-quorum.py` | 2-of-3 panel vs 3-of-5 quorum on C01–C20 |
| `TD2/Pair A/TD2_groupe_A.md` | write-up and tables |
| `TD2/vote-td2.jsonl`, `TD2/vote-2of3-vs-3of5.jsonl` | stored outputs |

Method: read the code against the docstring contract and the assignment, ran every command, recomputed both quorums on the twenty questions independently.

## Verdict

The vote is **correct** and the analysis is **accurate**: every value, vote count and change in the 2-of-3 vs 3-of-5 table matches our independent recomputation. One **blocking** issue: since the move to `TD2/Pair A/` (commit `bb6f3d3`), `vote-quorum.py` no longer runs, so the comparison table cannot be reproduced.

## What works (verified)

- **Contract of `vote_k_sur_n`**, checked case by case:
  - k = 1 and k = 4 refused for n = 3 (`ValueError`); strict majority `n // 2 < k <= n` checked before reading values.
  - Duplicate `(provider, model_requested)` refused, including between members in error.
  - Errors stay in n and cast no vote; an all-error panel abstains with 0 votes.
  - Abstention returns `value: None` and the largest count; no value is ever invented.
  - Reads both attribute objects (`atelier-vote.py`) and dicts.
- **Synthetic examples** (`python atelier-vote.py`): the four expected decisions, including the wrong consensus on 0.
- **2-of-3 table**: 17 consensus, all equal to the reference, 3 abstentions (C15, C17, C19), 10 unanimous decisions. Correct.
- **2-of-3 vs 3-of-5**: the two decision changes (C02 consensus → abstention, C19 abstention → consensus) and the margin-only cases (C09, C11, C18, C20) are correctly explained with values and verdicts from the traces.

## Issues

### 1. Blocking — `vote-quorum.py` crashes since the move

`TD2/Pair A/vote-quorum.py`, line 21, loads the skeleton next to the script:

```python
Path(__file__).with_name("skeleton-multi-llm-en.py")
```

After the move, this points to `TD2/Pair A/skeleton-multi-llm-en.py`, which does not exist:

```
FileNotFoundError: ... TD2/Pair A/skeleton-multi-llm-en.py
```

**Fix (tested, reproduces `TD2/vote-2of3-vs-3of5.jsonl` exactly):**

```python
Path(__file__).resolve().parents[2] / "skeleton-multi-llm-en.py"
```

### 2. Should fix — commands now point to a file that moved

The command `python vote-quorum.py --traces TD1/traces/traces-td1.csv` appears in `README.md` (Replay the TD 2 work), in `TD2/TD2.md` and in `TD2/Pair A/TD2_groupe_A.md`. It now fails with "No such file". Replace it by:

```
python "TD2/Pair A/vote-quorum.py" --traces TD1/traces/traces-td1.csv
```

The quotes are required because of the space in `Pair A`. Also update the repository layout in `README.md` (`vote-quorum.py` is no longer at the root).

### 3. Should fix — outputs and write-up are in different folders

`TD2_groupe_A.md` and `vote-quorum.py` are in `TD2/Pair A/`, but their outputs `vote-td2.jsonl` and `vote-2of3-vs-3of5.jsonl` stayed in `TD2/`. Either move the outputs next to the script (and update the paths in the commands), or keep everything in `TD2/`. One rule for the three groups would make the folder easier to read.

### 4. Minor — stored outputs start with a UTF-8 BOM

Both `.jsonl` files were written with PowerShell `Out-File -Encoding utf8`, which adds a BOM. `json.loads` on the first line read with `encoding="utf-8"` fails:

```
JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

Readers must use `utf-8-sig`, or the files can be regenerated without BOM (`python ... > file` from `cmd`, or `Out-File -Encoding utf8NoBOM` in PowerShell 7).

### 5. Minor — reproduction commands are PowerShell only

`TD2_groupe_A.md` (l. 119) uses `foreach ($i in 1..20) { ... }`. The README promises commands for Windows, macOS and Linux. `vote-quorum.py` already covers the twenty questions in one call; the `foreach` loop could be replaced by it, or a bash equivalent added.

### 6. Minor — code hygiene in `vote_k_sur_n`

- Comments in French (l. 636–666) while the repository is in English.
- Dead line l. 668: `#raise NotImplementedError(...)`, with a broken indentation. It can be deleted.
- `max(ballots.items(), key=...)` picks the first value on a tie. This is harmless because a tie can never reach a strict-majority k, but a one-line comment would avoid the question during the quiz.

### 7. Remark — 3-of-5 panel and model families

The 3-of-5 quorum includes `gpt-oss-120b` and `gpt-oss-20b`, two models of the same family. This is what the assignment asks (all five TD 1 models), but the write-up could say it explicitly: on C15 and C17 the only two agreeing votes come from that family.

## Assignment checklist

| Expected (Step 1) | Status |
|---|---|
| `vote_k_sur_n` completed, contract respected | ✔ |
| Four synthetic examples run | ✔ |
| Twenty-question table, 2-of-3 panel | ✔ |
| 3-of-5 quorum over the five TD 1 models, side by side | ✔ table correct, but **not reproducible** until issue 1 is fixed |
| Explanation of every decision change (C02, C19) and of margin changes (429, invalid SQL) | ✔ |
| Reproducible commands | ✘ issues 1 and 2 |

## Questions for the cross-review

1. Why must k satisfy `n // 2 < k`, and what would break with k = 2 for n = 4?
2. On C18 and C20, `qwen3.8-27b` is not executed: why does it stay in n, and what does the 2-of-3 decision rest on?
3. Why does C19 become a consensus with 3-of-5 while C15 and C17 stay abstentions?
