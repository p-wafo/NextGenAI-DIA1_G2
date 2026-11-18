-- TD 2, Pair B: delta diagnostic for the wrong consensus on C02.
-- One row per customer whose revenue differs between the reference query and
-- at least one faulty query. Each CASE copies the WHERE clause of one query,
-- evaluated order line by order line, so a row shows both missed revenue
-- (reference > faulty) and wrongly added revenue (faulty > reference).
SELECT
    c.customer_id,
    c.birth_date,
    -- Order lines selected by the reference filter
    SUM(CASE WHEN c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25'
             THEN 1 ELSE 0 END) AS reference_order_lines,
    -- Reference (reference-td1.csv): exactly 25 years old on 2026-09-25
    SUM(CASE WHEN c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25'
             THEN o.quantity_product * p.price ELSE 0 END) AS reference_cents,
    -- Faulty query 1, openai/gpt-oss-20b
    SUM(CASE WHEN c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25'
             THEN o.quantity_product * p.price ELSE 0 END) AS gpt_oss_20b_cents,
    -- Faulty query 2, dots-studio/dots-3-note-preview:free
    SUM(CASE WHEN CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
              AND substr(c.birth_date, 6, 2) = '09'
              AND substr(c.birth_date, 9, 2) = '25'
              AND o.date >= '2026-09-25 00:00:00'
              AND o.date <  '2026-09-26 00:00:00'
             THEN o.quantity_product * p.price ELSE 0 END) AS dots_cents
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN product   p ON p.product_id  = o.product_id
GROUP BY c.customer_id, c.birth_date
HAVING reference_cents <> gpt_oss_20b_cents OR reference_cents <> dots_cents
ORDER BY c.birth_date;
