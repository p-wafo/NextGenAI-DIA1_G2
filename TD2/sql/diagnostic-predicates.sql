-- Pourquoi les requêtes donnent-elles zéro sur cette base ?
SELECT
  (SELECT MIN(date) FROM orders) AS first_order,
  (SELECT MAX(date) FROM orders) AS last_order,
  (SELECT COUNT(*) FROM customers
   WHERE birth_date > '2025-09-25' AND birth_date <= '2026-09-25') AS m1_customers,
  (SELECT COUNT(*) FROM customers
   WHERE birth_date = '2001-09-25') AS m2_birthday_customers,
  (SELECT COUNT(*) FROM orders
   WHERE date >= '2026-09-25 00:00:00' AND date < '2026-09-26 00:00:00') AS m2_order_lines;
