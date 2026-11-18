-- Une ligne de commande = (order_id, product_id), pas seulement order_id.
-- Chaque indicateur reprend exactement le WHERE de la requête concernée.
WITH lignes AS (
    SELECT c.customer_id, c.birth_date, o.order_id, o.product_id,
           o.quantity_product * p.price AS amount_cents,
           CASE WHEN c.birth_date > '2000-09-25'
                 AND c.birth_date <= '2001-09-25' THEN 1 ELSE 0 END AS ref,
           CASE WHEN c.birth_date > '2025-09-25'
                 AND c.birth_date <= '2026-09-25' THEN 1 ELSE 0 END AS m1,
           CASE WHEN CAST(substr(c.birth_date, 1, 4) AS INTEGER) + 25 = 2026
                 AND substr(c.birth_date, 6, 2) = '09'
                 AND substr(c.birth_date, 9, 2) = '25'
                 AND o.date >= '2026-09-25 00:00:00'
                 AND o.date < '2026-09-26 00:00:00' THEN 1 ELSE 0 END AS m2
    FROM orders o
    JOIN customers c ON c.customer_id = o.customer_id
    JOIN product p ON p.product_id = o.product_id
)
SELECT customer_id, birth_date,
       SUM(ref) AS reference_order_lines,
       SUM(amount_cents * ref) AS reference_cents,
       SUM(amount_cents * m1) AS m1_cents,
       SUM(amount_cents * m2) AS m2_cents,
       SUM(amount_cents * (ref - m1)) AS delta_m1_cents,
       SUM(amount_cents * (ref - m2)) AS delta_m2_cents
FROM lignes
GROUP BY customer_id, birth_date
HAVING SUM(CASE WHEN ref != m1 OR ref != m2 THEN 1 ELSE 0 END) > 0
ORDER BY customer_id;
