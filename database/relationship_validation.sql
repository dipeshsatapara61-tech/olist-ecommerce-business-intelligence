-- Data Quality and Relationship Validation Queries

-- 1. Total record count per table
SELECT 'customers' AS table_name, COUNT(*) AS total_records FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL SELECT 'category_translation', COUNT(*) FROM category_translation
UNION ALL SELECT 'geolocation', COUNT(*) FROM geolocation
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'payments', COUNT(*) FROM payments
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews
ORDER BY total_records DESC;

-- 2. Check for orphan orders (orders without a matching customer)
SELECT
    COUNT(*) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS unique_customers,
    COUNT(*) FILTER (WHERE c.customer_id IS NULL) AS orphan_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id;

-- 3. Check for invalid order items (missing order, product, or seller)
SELECT
    COUNT(*) AS total_order_items,
    COUNT(*) FILTER (WHERE o.order_id IS NULL) AS missing_orders,
    COUNT(*) FILTER (WHERE p.product_id IS NULL) AS missing_products,
    COUNT(*) FILTER (WHERE s.seller_id IS NULL) AS missing_sellers
FROM order_items oi
LEFT JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
LEFT JOIN sellers s ON oi.seller_id = s.seller_id;

-- 4. Check for orphan payments and reviews
SELECT
    'payments' AS dataset,
    COUNT(*) AS total_records,
    COUNT(*) FILTER (WHERE o.order_id IS NULL) AS orphan_records
FROM payments p
LEFT JOIN orders o ON p.order_id = o.order_id
UNION ALL
SELECT
    'reviews',
    COUNT(*),
    COUNT(*) FILTER (WHERE o.order_id IS NULL)
FROM reviews r
LEFT JOIN orders o ON r.order_id = o.order_id;

-- 5. Validate composite primary keys
SELECT
    'order_items (order_id, order_item_id)' AS composite_key,
    COUNT(*) AS total_rows,
    COUNT(*) - COUNT(DISTINCT (order_id, order_item_id)) AS duplicate_keys
FROM order_items
UNION ALL
SELECT
    'payments (order_id, payment_sequential)',
    COUNT(*),
    COUNT(*) - COUNT(DISTINCT (order_id, payment_sequential))
FROM payments
UNION ALL
SELECT
    'reviews (review_id, order_id)',
    COUNT(*),
    COUNT(*) - COUNT(DISTINCT (review_id, order_id))
FROM reviews;

-- 6. Check product categories and translation mapping
SELECT
    COUNT(*) AS total_products,
    COUNT(*) FILTER (WHERE p.product_category_name IS NULL) AS missing_categories,
    COUNT(*) FILTER (
        WHERE p.product_category_name IS NOT NULL
          AND ct.product_category_name IS NULL
    ) AS untranslated_categories
FROM products p
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name;

-- 7. Check order lifecycle chronological sequence
SELECT
    COUNT(*) AS total_delivered_orders,
    COUNT(*) FILTER (WHERE order_approved_at < order_purchase_timestamp) AS approved_before_purchase,
    COUNT(*) FILTER (WHERE order_delivered_carrier_date < order_purchase_timestamp) AS carrier_before_purchase,
    COUNT(*) FILTER (WHERE order_delivered_customer_date < order_delivered_carrier_date) AS customer_before_carrier
FROM orders
WHERE order_status = 'delivered';

-- 8. Order status vs delivery date check
SELECT
    order_status,
    COUNT(*) AS total_orders,
    COUNT(order_delivered_customer_date) AS orders_with_delivery_date,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 9. Check ZIP code match rate with geolocation table
SELECT
    'Customer ZIP Codes' AS entity,
    COUNT(DISTINCT c.customer_zip_code_prefix) AS distinct_zip_codes,
    COUNT(DISTINCT g.geolocation_zip_code_prefix) AS matched_in_geo,
    ROUND(COUNT(DISTINCT g.geolocation_zip_code_prefix) * 100.0 / COUNT(DISTINCT c.customer_zip_code_prefix), 2) AS match_pct
FROM customers c
LEFT JOIN geolocation g ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix
UNION ALL
SELECT
    'Seller ZIP Codes',
    COUNT(DISTINCT s.seller_zip_code_prefix),
    COUNT(DISTINCT g.geolocation_zip_code_prefix),
    ROUND(COUNT(DISTINCT g.geolocation_zip_code_prefix) * 100.0 / COUNT(DISTINCT s.seller_zip_code_prefix), 2)
FROM sellers s
LEFT JOIN geolocation g ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix;
