-- C02, Dots: the order-date clause of the returned query, alone (birth-date clause removed).
-- Isolates the second faulty clause: orders restricted to 2026-09-25, not asked by the question.
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN product p ON o.product_id = p.product_id
WHERE o.date >= '2026-09-25 00:00:00'
  AND o.date <  '2026-09-26 00:00:00';
