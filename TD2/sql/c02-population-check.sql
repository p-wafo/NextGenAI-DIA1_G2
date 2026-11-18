-- Population check: how many customers and order lines each WHERE clause selects.
-- An amount of 0 with a non-empty reference population is suspect and must be escalated.
-- C06 and C14 are true zeros: their reference population is empty too.
SELECT 'C02 reference' AS filter, COUNT(DISTINCT c.customer_id) AS customers, COUNT(o.order_id) AS order_lines
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
WHERE c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25'
UNION ALL
SELECT 'C02 GPT-OSS 20B', COUNT(DISTINCT c.customer_id), COUNT(o.order_id)
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
WHERE c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25'
UNION ALL
SELECT 'C02 Dots', COUNT(DISTINCT c.customer_id), COUNT(o.order_id)
FROM orders o JOIN customers c ON c.customer_id = o.customer_id
WHERE CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
  AND substr(c.birth_date, 6, 2) = '09' AND substr(c.birth_date, 9, 2) = '25'
  AND o.date >= '2026-09-25 00:00:00' AND o.date < '2026-09-26 00:00:00'
UNION ALL
SELECT 'C06 reference (true zero)', COUNT(DISTINCT o.customer_id), COUNT(o.order_id)
FROM orders o
WHERE o.date >= '2025-01-01 00:00:00' AND o.date < '2026-01-01 00:00:00'
UNION ALL
SELECT 'C14 reference (true zero)', COUNT(DISTINCT o.customer_id), COUNT(o.order_id)
FROM orders o
WHERE o.date >= '2026-10-01 00:00:00' AND o.date < '2026-12-01 00:00:00'
  AND o.product_id IN ('a', 'b', 'c');
