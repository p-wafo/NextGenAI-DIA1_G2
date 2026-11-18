"""Reproduce Pair B on the committed TD1 traces and shop data, offline."""
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SQL = ROOT / 'TD2/sql'


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def csv_totals():
    reference_day = date(2026, 9, 25)
    births = {r['customer_id']: date.fromisoformat(r['birth_date']) for r in read_csv(DATA / 'customers.csv')}
    prices = {r['product_id']: int(r['price']) for r in read_csv(DATA / 'product.csv')}
    totals, counts = Counter(), Counter()
    for order in read_csv(DATA / 'orders.csv'):
        customer = order['customer_id']
        born = births[customer]
        birthday_passed = (born.month, born.day) <= (reference_day.month, reference_day.day)
        age = reference_day.year - born.year - (not birthday_passed)
        if age == 25:
            totals[customer] += int(order['quantity_product']) * prices[order['product_id']]
            counts[customer] += 1
    return totals, counts


def main():
    traces = read_csv(ROOT / 'TD1/traces/traces-td1.csv')
    latest = {(r['case_id'], r['provider'], r['model_requested']): r for r in traces if r['nature'] == 'real'}
    check(len(latest) == 100, 'Expected 100 real final cells')
    wrong = defaultdict(list)
    for (case, provider, model), row in latest.items():
        if row['verdict'] == 'incorrect':
            wrong[case, int(row['value'])].append(f'{provider}:{model}')
    shared = [{'case': case, 'value': value, 'models': sorted(models)}
              for (case, value), models in sorted(wrong.items()) if len(models) >= 2]
    check(len(shared) == 1 and shared[0]['case'] == 'C02' and shared[0]['value'] == 0,
          'Unexpected shared wrong case')
    reference = next(r for r in read_csv(ROOT / 'TD1/reference-td1.csv') if r['case_id'] == 'C02')
    expected = int(reference['revenue_cents'])
    models = {'m1-gpt20b.sql': ('groq', 'openai/gpt-oss-20b'),
              'm2-dots.sql': ('openrouter', 'dots-studio/dots-3-note-preview:free')}
    database = (DATA / 'boutique.sqlite').as_uri() + '?mode=ro'
    with closing(sqlite3.connect(database, uri=True)) as db:
        db.execute('PRAGMA query_only = ON')
        db.row_factory = sqlite3.Row

        def execute(filename):
            return db.execute((SQL / filename).read_text(encoding='utf-8')).fetchall()

        values = {}
        for filename, (provider, model) in models.items():
            row = latest['C02', provider, model]
            traced_sql = row['sql'].replace('\r\n', '\n').strip()
            check(traced_sql == (SQL / filename).read_text(encoding='utf-8').strip(), 'SQL differs from trace')
            values[model] = execute(filename)[0][0]
            check(values[model] == int(row['value']), 'SQL result differs from trace')
        check(expected == db.execute(reference['sql']).fetchone()[0] == execute('reference-c02.sql')[0][0],
              'Reference SQL results differ')
        delta = [dict(row) for row in execute('delta-c02.sql')]
        predicates = dict(execute('diagnostic-predicates.sql')[0])
        filter_checks = dict(execute('diagnostic-m2.sql')[0])

    totals, counts = csv_totals()
    check(dict(totals) == {r['customer_id']: r['reference_cents'] for r in delta}, 'Customer totals differ')
    check(dict(counts) == {r['customer_id']: r['reference_order_lines'] for r in delta}, 'Line counts differ')
    check(sum(totals.values()) == expected, 'CSV and SQL reference differ')
    for column, model in zip(('delta_m1_cents', 'delta_m2_cents'), values):
        check(sum(r[column] for r in delta) == expected - values[model], f'Incomplete delta for {model}')
    print(json.dumps(dict(trace_records=len(traces), final_cells=len(latest), shared_wrong_values=shared,
                          reference_cents=expected, replayed_values=values, order_lines=sum(counts.values()),
                          customer_delta=delta, predicates=predicates, filter_checks=filter_checks), indent=2))


if __name__ == '__main__':
    main()
