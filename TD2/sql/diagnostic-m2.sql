-- Séparer les deux défauts de M2 sans créer de nouvelles réponses de modèles.
SELECT
  COALESCE(SUM(CASE WHEN c.birth_date = '2001-09-25'
                    THEN o.quantity_product * p.price ELSE 0 END), 0)
    AS birthday_only_all_orders_cents,
  COALESCE(SUM(CASE WHEN c.birth_date > '2000-09-25'
                    AND c.birth_date <= '2001-09-25'
                    AND o.date >= '2026-09-25 00:00:00'
                    AND o.date < '2026-09-26 00:00:00'
                    THEN o.quantity_product * p.price ELSE 0 END), 0)
    AS correct_age_wrong_order_window_cents,
  COALESCE(SUM(CASE WHEN c.birth_date > '2000-09-25'
                    AND c.birth_date <= '2001-09-25'
                    THEN o.quantity_product * p.price ELSE 0 END), 0)
    AS correct_age_all_orders_cents
FROM orders o
JOIN customers c ON c.customer_id = o.customer_id
JOIN product p ON p.product_id = o.product_id;
