-- C02, Dots: correct age window, but Dots' order-day filter kept (contribution of Hugo HOUPPE).
-- Shows that the order-date clause alone is enough to empty the result.
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2000-09-25' AND c.birth_date <= '2001-09-25'
  AND o.date >= '2026-09-25 00:00:00'
  AND o.date <  '2026-09-26 00:00:00';
