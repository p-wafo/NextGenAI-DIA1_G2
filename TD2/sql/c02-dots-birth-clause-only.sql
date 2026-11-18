-- C02, Dots: the birth-date clause of the returned query, alone (order-date clause removed).
-- Isolates the first faulty clause: one birth date instead of a one-year window.
SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
  AND substr(c.birth_date, 6, 2) = '09'
  AND substr(c.birth_date, 9, 2) = '25';
