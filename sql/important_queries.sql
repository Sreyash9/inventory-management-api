-- ============================================================
-- Inventory API — Important SQL Queries
-- ============================================================
-- These are the hand-written SQL queries referenced in the README's
-- "Database Deliverables" section. The category rollup query below is
-- executed at runtime via repositories/product_repository.py
-- (ProductRepository.get_category_summary), served by
-- GET /reports/category-summary.
-- ============================================================


-- ------------------------------------------------------------
-- 1. Category rollup report
--    Returns: category, product_count, total_stock, inventory_value
--    Uses a LEFT JOIN so categories with zero products still appear
--    (with product_count/total_stock/inventory_value = 0), and
--    COALESCE guards against NULLs from the aggregate over no rows.
-- ------------------------------------------------------------
SELECT
    c.id                                       AS category_id,
    c.name                                      AS category_name,
    COUNT(p.id)                                  AS product_count,
    COALESCE(SUM(p.quantity), 0)                 AS total_stock,
    COALESCE(SUM(p.price * p.quantity), 0)       AS inventory_value
FROM categories c
LEFT JOIN products p ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY c.name;


-- ------------------------------------------------------------
-- 2. Low stock products (ad-hoc equivalent of GET /products/low-stock)
--    The API implements this via the ORM (see
--    ProductRepository.list_low_stock), but the equivalent raw SQL is:
-- ------------------------------------------------------------
SELECT id, name, sku, category_id, price, quantity
FROM products
WHERE quantity < :threshold   -- e.g. 10
ORDER BY quantity ASC;


-- ------------------------------------------------------------
-- 3. Products joined with their category name
--    Useful for a denormalized listing view.
-- ------------------------------------------------------------
SELECT
    p.id,
    p.name,
    p.sku,
    c.name  AS category_name,
    p.price,
    p.quantity,
    (p.price * p.quantity) AS line_value
FROM products p
JOIN categories c ON c.id = p.category_id
ORDER BY p.name;


-- ------------------------------------------------------------
-- 4. Single most valuable category by total inventory value
--    (an extension of query #1, useful for a "top category" widget)
-- ------------------------------------------------------------
SELECT
    c.name AS category_name,
    COALESCE(SUM(p.price * p.quantity), 0) AS inventory_value
FROM categories c
LEFT JOIN products p ON p.category_id = c.id
GROUP BY c.id, c.name
ORDER BY inventory_value DESC
LIMIT 1;
