#!/usr/bin/env python3
"""TD 2 Step 1: compare the fixed 2-of-3 panel and the 3-of-5 quorum on the TD 1 traces.

Uses Orchestrateur.vote_k_sur_n from skeleton-multi-llm-en.py (same loader as atelier-vote.py).
No network. The reference is compared AFTER the decision.

    python vote-quorum.py --traces TD1/traces/traces-td1.csv
"""
import argparse, csv, importlib.util, json, sys
from pathlib import Path
from types import SimpleNamespace

PANEL_3 = [("groq", "openai/gpt-oss-120b"),
           ("openrouter", "cohere/north-mini-code:free"),
           ("groq", "qwen/qwen3.8-27b")]
PANEL_5 = PANEL_3 + [("groq", "openai/gpt-oss-20b"),
                     ("openrouter", "dots-studio/dots-3-note-preview:free")]


def load_vote():
    spec = importlib.util.spec_from_file_location("student_skeleton", Path(__file__).with_name("skeleton-multi-llm-en.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return lambda proposals, k: module.Orchestrateur.vote_k_sur_n(None, proposals, k)


def proposals_for(rows, case, panel):
    """Same rule as atelier-vote.py: last attempt per member; an error keeps its place without a vote."""
    selected = {}
    for row in rows:
        key = (row["provider"], row["model_requested"])
        if row["case_id"] == case and row["nature"] == "real" and key in panel:
            selected[key] = row
    proposals = []
    for provider, model in panel:
        row = selected.get((provider, model), {})
        value = row.get("value", "")
        valid = row.get("verdict") in {"correct", "incorrect"} and value not in {None, ""}
        proposals.append(SimpleNamespace(provider=provider, model_requested=model,
                                         value=int(value) if valid else None,
                                         verdict="executed" if valid else "error"))
    return proposals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=Path, required=True)
    args = parser.parse_args()
    vote = load_vote()
    with args.traces.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for i in range(1, 21):
        case = f"C{i:02d}"
        refs = {int(r["reference"]) for r in rows if r["case_id"] == case and r.get("reference") not in {None, ""}}
        if len(refs) != 1:
            raise SystemExit(f"{case}: expected one reference, found {refs}")
        ref = refs.pop()
        out = {"case": case, "reference": ref}
        for label, panel, k in (("2of3", PANEL_3, 2), ("3of5", PANEL_5, 3)):
            d = vote(proposals_for(rows, case, panel), k)
            out[label] = {"consensus": d["consensus"], "value": d["value"], "votes": d["votes"],
                          "matches_reference": (d["value"] == ref) if d["consensus"] else None}
        print(json.dumps(out))


if __name__ == "__main__":
    main()
