-- C02, openai/gpt-oss-20b: query as returned in TD 1 (traces-td1.csv), executed unchanged
SELECT COALESCE(SUM(o.quantity_product * p.price),0) AS revenue_cents
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN product p ON o.product_id = p.product_id
WHERE c.birth_date > '2025-09-25' AND c.birth_date <= '2026-09-25';
