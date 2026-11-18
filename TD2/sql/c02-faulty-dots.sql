-- C02, dots-studio/dots-3-note-preview:free: query as returned in TD 1 (traces-td1.csv), executed unchanged
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE (
    CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
    AND substr(c.birth_date, 6, 2) = '09'
    AND substr(c.birth_date, 9, 2) = '25'
)
AND o.date >= '2026-09-25 00:00:00'
AND o.date < '2026-09-26 00:00:00';
