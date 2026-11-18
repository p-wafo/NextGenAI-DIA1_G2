-- Total of the delta: must equal reference (590320) minus the shared wrong value (0).
SELECT COUNT(*)                              AS customers,
       SUM(reference_cents)                  AS reference_cents,
       SUM(gpt_oss_20b_cents)                AS gpt_oss_20b_cents,
       SUM(dots_cents)                       AS dots_cents,
       SUM(reference_cents - gpt_oss_20b_cents) AS gap_gpt_oss_20b,
       SUM(reference_cents - dots_cents)     AS gap_dots
FROM (
    SELECT c.customer_id,
        SUM(CASE WHEN c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25'
                 THEN o.quantity_product * p.price ELSE 0 END) AS reference_cents,
        SUM(CASE WHEN c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25'
                 THEN o.quantity_product * p.price ELSE 0 END) AS gpt_oss_20b_cents,
        SUM(CASE WHEN CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
                  AND substr(c.birth_date, 6, 2) = '09' AND substr(c.birth_date, 9, 2) = '25'
                  AND o.date >= '2026-09-25 00:00:00' AND o.date < '2026-09-26 00:00:00'
                 THEN o.quantity_product * p.price ELSE 0 END) AS dots_cents
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN product   p ON p.product_id  = o.product_id
    GROUP BY c.customer_id
) AS per_customer
WHERE reference_cents <> gpt_oss_20b_cents OR reference_cents <> dots_cents;
