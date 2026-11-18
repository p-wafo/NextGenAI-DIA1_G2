#!/usr/bin/env python3
"""TD 2, Pair B: reproduce every figure of TD2/wrong-consensus.md, read-only, offline.

Run from the repository root:
    python TD2/pair_b_check.py
    python TD2/pair_b_check.py > TD2/pair_b_check-output.txt

Steps: database fingerprint, search for shared wrong values in the TD 1 traces,
votes with the group's vote_k_sur_n (fixed 2-of-3 panel and 3-of-5 quorum), the
SQL files of TD2/sql, an independent recomputation on the CSV files, and the
DEMO-VOTE toy table. No network, no key, no write to data/boutique.sqlite.
Standard library only.
"""
import csv
import datetime
import hashlib
import importlib.util
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DB = DATA / "boutique.sqlite"
SQL = Path(__file__).resolve().parent / "sql"
TRACES = ROOT / "TD1" / "traces" / "traces-td1.csv"
CASE = "C02"
REFERENCE_DATE = datetime.date(2026, 9, 25)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def completed_age(birth, on):
    b = datetime.date.fromisoformat(birth[:10])
    return on.year - b.year - ((on.month, on.day) < (b.month, b.day))


def title(text):
    print(f"\n## {text}")


def main():
    title("0. Database fingerprint")
    expected = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))["sqlite_file_sha256"]
    observed = sha256(DB)
    print(f"[{'OK' if observed == expected else 'KO'}] boutique.sqlite sha256 {observed[:8]}...{observed[-8:]} (manifest {expected[:8]}...{expected[-8:]})")

    title("1. Shared wrong values in TD1/traces/traces-td1.csv")
    with TRACES.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    print(f"{len(rows)} rows, natures: {sorted({r['nature'] for r in rows})}")
    shared = defaultdict(set)
    for row in rows:
        if row["verdict"] == "incorrect":
            shared[(row["case_id"], row["value"])].add(f"{row['provider']}:{row['model_requested']}")
    for (case, value), models in sorted(shared.items()):
        if len(models) >= 2:
            print(f"shared wrong value: {case} value={value} models={sorted(models)}")
    for number, row in enumerate(rows, start=2):
        if row["case_id"] == CASE:
            print(f"  table row {number}: {row['cell_id']} value={row['value']} reference={row['reference']} "
                  f"verdict={row['verdict']} attempts={row['attempts']} http={row['http_status']} prompt_sha256={row['prompt_sha256'][:12]}...")

    title("2. Votes on C02 with the group's vote_k_sur_n")
    vote_module = load(ROOT / "atelier-vote.py", "atelier_vote")
    vote = vote_module.load_vote()
    panel = vote_module.proposals_for(rows, CASE, "real")
    print("fixed panel 2 of 3:", [(p.model_requested, p.value) for p in panel])
    print("  ->", json.dumps(vote(panel, 2)))
    last = {}
    for row in rows:
        if row["case_id"] == CASE and row["nature"] == "real":
            last[(row["provider"], row["model_requested"])] = row
    five = []
    for (provider, model), row in last.items():
        valid = row["verdict"] in {"correct", "incorrect"} and row["value"] != ""
        five.append(SimpleNamespace(provider=provider, model_requested=model,
                                    value=int(row["value"]) if valid else None,
                                    verdict="executed" if valid else "error"))
    print("five TD 1 models 3 of 5:", [(p.model_requested, p.value) for p in five])
    print("  ->", json.dumps(vote(five, 3)))

    title("3. SQL files of TD2/sql on data/boutique.sqlite (read-only)")
    con = sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True)
    for name in ["c02-reference.sql", "c02-faulty-gpt-oss-20b.sql", "c02-faulty-dots.sql",
                 "c02-dots-birth-clause-only.sql", "c02-dots-date-clause-only.sql"]:
        print(f"{name:34} -> {con.execute((SQL / name).read_text(encoding='utf-8')).fetchone()[0]}")
    for name in ["c02-delta.sql", "c02-delta-total.sql", "c02-population-check.sql"]:
        cursor = con.execute((SQL / name).read_text(encoding="utf-8"))
        print(f"{name}: " + " | ".join(d[0] for d in cursor.description))
        for record in cursor.fetchall():
            print("   " + " | ".join(str(x) for x in record))
    print("birth_date range:", con.execute("SELECT MIN(birth_date), MAX(birth_date) FROM customers").fetchone())
    print("order date range:", con.execute("SELECT MIN(date), MAX(date) FROM orders").fetchone())
    con.close()

    title("4. Independent recomputation on the CSV files (completed age in Python, no SQL)")
    price = {r["product_id"]: int(r["price"]) for r in csv.DictReader((DATA / "product.csv").open(encoding="utf-8"))}
    birth = {r["customer_id"]: r["birth_date"] for r in csv.DictReader((DATA / "customers.csv").open(encoding="utf-8"))}
    totals, lines = defaultdict(int), 0
    for order in csv.DictReader((DATA / "orders.csv").open(encoding="utf-8")):
        if completed_age(birth[order["customer_id"]], REFERENCE_DATE) == 25:
            totals[order["customer_id"]] += int(order["quantity_product"]) * price[order["product_id"]]
            lines += 1
    for customer in sorted(totals, key=lambda c: birth[c]):
        print(f"   {customer} | {birth[customer]} | {totals[customer]}")
    print(f"customers={len(totals)} order_lines={lines} total={sum(totals.values())}")

    title("5. DEMO-VOTE toy table (synthetic teaching material, not shop data)")
    toy = sqlite3.connect(":memory:")
    toy.execute("CREATE TABLE sales (sale_date TEXT, amount_cents INTEGER)")
    toy.execute("INSERT INTO sales VALUES ('2026-01-01', 100)")
    values = []
    for operator in (">", ">", ">="):
        values.append(toy.execute(f"SELECT COALESCE(SUM(amount_cents), 0) FROM sales "
                                  f"WHERE sale_date {operator} '2026-01-01' AND sale_date < '2026-01-02'").fetchone()[0])
    print("proposals:", values, "reference: 100")
    proposals = [SimpleNamespace(provider=p, model_requested=m, value=v, verdict="executed")
                 for (p, m), v in zip(vote_module.PANEL, values)]
    print("  2 of 3 ->", json.dumps(vote(proposals, 2)))


if __name__ == "__main__":
    main()
