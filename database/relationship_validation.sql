
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    COUNT(*) FILTER (
        WHERE c.customer_id IS NULL
    ) AS orphan_orders
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id;







SELECT
    COUNT(*) AS total_order_items,

    COUNT(*) FILTER (
        WHERE o.order_id IS NULL
    ) AS missing_orders,

    COUNT(*) FILTER (
        WHERE p.product_id IS NULL
    ) AS missing_products,

    COUNT(*) FILTER (
        WHERE s.seller_id IS NULL
    ) AS missing_sellers

FROM order_items oi

LEFT JOIN orders o
    ON oi.order_id = o.order_id

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN sellers s
    ON oi.seller_id = s.seller_id;














SELECT
    'customers' AS table_name,
    COUNT(*) AS total_records
FROM customers

UNION ALL

SELECT 'products', COUNT(*) FROM products

UNION ALL

SELECT 'sellers', COUNT(*) FROM sellers

UNION ALL

SELECT 'category_translation', COUNT(*)
FROM category_translation

UNION ALL

SELECT 'geolocation', COUNT(*) FROM geolocation

UNION ALL

SELECT 'orders', COUNT(*) FROM orders

UNION ALL

SELECT 'order_items', COUNT(*) FROM order_items

UNION ALL

SELECT 'payments', COUNT(*) FROM payments

UNION ALL

SELECT 'reviews', COUNT(*) FROM reviews;












SELECT
    'Payments' AS dataset,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (
        WHERE o.order_id IS NULL
    ) AS orphan_records
FROM payments p
LEFT JOIN orders o
    ON p.order_id = o.order_id

UNION ALL





SELECT
    'Reviews',
    COUNT(*),
    COUNT(*) FILTER (
        WHERE o.order_id IS NULL
    )
FROM reviews r
LEFT JOIN orders o
    ON r.order_id = o.order_id;










	SELECT
    COUNT(*) AS total_products,
    COUNT(*) FILTER (
        WHERE p.product_category_name IS NULL
    ) AS missing_categories,
    COUNT(*) FILTER (
        WHERE p.product_category_name IS NOT NULL
        AND ct.product_category_name IS NULL
    ) AS untranslated_categories

FROM products p

LEFT JOIN category_translation ct
    ON p.product_category_name =
       ct.product_category_name;










	   SELECT
    COUNT(*) AS total_reviews,
    COUNT(DISTINCT (review_id, order_id))
        AS unique_review_combinations
FROM reviews;









SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM orders),
        2
    ) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;
 