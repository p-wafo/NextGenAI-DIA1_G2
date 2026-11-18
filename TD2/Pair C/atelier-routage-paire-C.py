#!/usr/bin/env python3
"""TD 2, Pair C: routing rule adapted from atelier-routage.py.

Synthetic simulation, no API call, no key.

Resources are the five models of the DIA1-G2 TD 1 batch. A resource is
eligible for a question family only if its last attempt was correct on every
cell of that family in TD 1 (TD1/results/pivot-view.md).

Cash is a fictional cost per request, computed from the documented paid list
price (TD1/results/five-model-summary-en.csv) with a fixed token envelope.
Quota availability is supplied by the scenario, not measured from a provider.
"""
import argparse
import json

# Fixed token envelope per request (order of magnitude, assumption to check
# against the token columns of TD1/traces/traces-td1.csv).
ENVELOPE_IN = 2000
ENVELOPE_OUT = 300

FAMILIES = {
    "F1": "period (C01, C04, C05, C06, C07, C20)",
    "F2": "completed age at a date (C02, C08, C09, C11)",
    "F2b": "age at the order (C10)",
    "F3": "product list (C03, C12, C13, C14)",
    "COMB": "combinations (C15 to C19)",
}


def cash(price_in, price_out):
    """Fictional USD excluding tax for one request with the fixed envelope."""
    return round(ENVELOPE_IN * price_in / 1e6 + ENVELOPE_OUT * price_out / 1e6, 6)


# Families where the model was 100 % correct in TD 1, with the observed ratio.
COHERE = {"F1": "6/6", "F3": "4/4"}
DOTS = {"F1": "6/6", "F3": "4/4"}
OSS_20B = {"F1": "6/6", "F2b": "1/1", "F3": "4/4", "COMB": "5/5"}   # F2 3/4, C02 wrong
OSS_120B = {"F1": "6/6", "F2": "4/4", "F2b": "1/1", "F3": "4/4", "COMB": "5/5"}
QWEN = {"F2": "4/4", "F2b": "1/1", "F3": "4/4"}                     # F1 5/6 (C20 NE), COMB 0/5

RESOURCES = [
    # Free routes used in TD 1 (cash 0). list_price breaks ties between free routes.
    {"id": "cohere-north-mini-code-free", "provider": "openrouter", "access": "free",
     "families": COHERE, "list_price": 0.0, "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "dots-3-note-preview-free", "provider": "openrouter", "access": "free",
     "families": DOTS, "list_price": 0.0, "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "gpt-oss-20b-groq-free", "provider": "groq", "access": "free",
     "families": OSS_20B, "list_price": 0.075, "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "gpt-oss-120b-groq-free", "provider": "groq", "access": "free",
     "families": OSS_120B, "list_price": 0.15, "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    {"id": "qwen3.8-27b-groq-free", "provider": "groq", "access": "free",
     "families": QWEN, "list_price": 0.80, "available": True,
     "cash": 0.0, "allocation": 0.0, "reset_minutes": None},
    # Paid routes of the same models (Groq Developer). Cohere and Dots: no paid route (N/A).
    {"id": "gpt-oss-20b-groq-paid", "provider": "groq", "access": "tokens",
     "families": OSS_20B, "list_price": 0.075, "available": True,
     "cash": cash(0.075, 0.30), "allocation": cash(0.075, 0.30), "reset_minutes": None},
    {"id": "gpt-oss-120b-groq-paid", "provider": "groq", "access": "tokens",
     "families": OSS_120B, "list_price": 0.15, "available": True,
     "cash": cash(0.15, 0.60), "allocation": cash(0.15, 0.60), "reset_minutes": None},
    {"id": "qwen3.8-27b-groq-paid", "provider": "groq", "access": "tokens",
     "families": QWEN, "list_price": 0.80, "available": True,
     "cash": cash(0.80, 4.00), "allocation": cash(0.80, 4.00), "reset_minutes": None},
]

CHECKS = {
    "internal": "none (first model 100 % correct on the family in TD 1)",
    "customer": "2-of-3 quorum among models 100 % correct on the family",
    "payout": "reference SQL check and human review",
}


def checks_for(request):
    family, use = request["family"], request["use"]
    if family == "F2b" and use == "internal":
        return "2-of-3 quorum (F2b rests on C10 only)"
    if family == "COMB" and use == "customer":
        return "agreement of gpt-oss-20b and gpt-oss-120b plus reference SQL check"
    return CHECKS[use]


def evidence(resource, family):
    return f"TD 1 {family} {FAMILIES[family]}: {resource['id']} {resource['families'][family]}"


def choose(request, resources):
    """Pair C policy: cheapest eligible free route, then wait, then paid route, else abstain."""
    family = request["family"]
    eligible = [r for r in resources if family in r["families"]]
    checks = checks_for(request) if family in FAMILIES else CHECKS[request["use"]]
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["list_price"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "cheapest eligible free route; " + evidence(chosen, family)}
    waiting = [r for r in eligible if not r["available"] and r["cash"] == 0
               and r["reset_minutes"] is not None
               and 0 < r["reset_minutes"] <= request["deadline_minutes"]]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: (r["reset_minutes"], r["list_price"], r["id"]))
        return {"action": "defer", "resource": chosen["id"], "cash": 0, "checks": checks,
                "reason": "free route exhausted, recheck availability at wake-up; "
                          + evidence(chosen, family),
                "wake_in_minutes": chosen["reset_minutes"]}
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["id"]))
        return {"action": "run", "resource": chosen["id"], "cash": chosen["cash"], "checks": checks,
                "reason": "paid route of a model correct on the family, within budget; "
                          + evidence(chosen, family)}
    reason = ("no model 100 % correct on this family in TD 1" if not eligible
              else "no eligible resource within deadline and budget")
    return {"action": "abstain", "resource": None, "cash": 0, "checks": checks, "reason": reason}


def scenarios():
    base = {"family": "F1", "use": "internal", "can_wait": True,
            "deadline_minutes": 120, "budget": 0.30}
    # Groq Free routes rate-limited (HTTP 429 seen in TD 1), fictional refill in 60 minutes.
    exhausted = [dict(r, available=False, reset_minutes=60)
                 if r["provider"] == "groq" and r["access"] == "free" else dict(r)
                 for r in RESOURCES]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "family": "COMB"}, RESOURCES),
        ("deferrable", {**base, "family": "COMB"}, exhausted),
        ("urgent", {**base, "family": "COMB", "can_wait": False, "deadline_minutes": 5}, exhausted),
        ("budget exhausted", {**base, "family": "COMB", "can_wait": False, "budget": 0}, exhausted),
        ("high impact", {**base, "family": "F2", "use": "payout"}, RESOURCES),
        ("unknown capability", {**base, "family": "F4"}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({"scenario": name, "nature": "simulation", "request": request,
                          "result": choose(request, resources)}))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()
