-- Olist E-Commerce Business Analysis Queries

-- 1. Overall Business KPIs
SELECT
    ROUND(SUM(oi.price) + SUM(oi.freight_value), 2) AS total_revenue,
    ROUND(SUM(oi.price), 2) AS product_sales,
    ROUND(SUM(oi.freight_value), 2) AS total_freight,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    COUNT(DISTINCT oi.product_id) AS total_products,
    COUNT(DISTINCT oi.seller_id) AS total_sellers,
    ROUND((SUM(oi.price) + SUM(oi.freight_value)) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id;

-- 2. Monthly Revenue Trend and MoM Growth
WITH monthly AS (
    SELECT
        TO_CHAR(o.order_purchase_timestamp, 'YYYY-MM') AS month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.price + oi.freight_value), 2) AS revenue,
        ROUND((SUM(oi.price + oi.freight_value)) / COUNT(DISTINCT o.order_id), 2) AS aov
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY 1
)
SELECT
    month,
    total_orders,
    revenue,
    aov,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) / 
        NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- 3. Order Status Breakdown
SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 4. Revenue by Payment Method
SELECT
    payment_type,
    COUNT(order_id) AS transaction_count,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(SUM(payment_value) * 100.0 / SUM(SUM(payment_value)) OVER (), 2) AS share_pct,
    ROUND(AVG(payment_installments), 1) AS avg_installments
FROM payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;

-- 5. Top 10 Product Categories by Revenue
SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name, 'Uncategorized') AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS product_sales,
    ROUND(SUM(oi.freight_value), 2) AS freight_fees,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS avg_item_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1
ORDER BY total_revenue DESC
LIMIT 10;

-- 6. Product Categories with Highest Freight %
SELECT
    COALESCE(ct.product_category_name_english, p.product_category_name, 'Uncategorized') AS category,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price), 2) AS product_sales,
    ROUND(SUM(oi.freight_value), 2) AS freight_fees,
    ROUND(SUM(oi.freight_value) * 100.0 / NULLIF(SUM(oi.price + oi.freight_value), 0), 2) AS freight_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY 1
HAVING COUNT(oi.order_item_id) >= 100
ORDER BY freight_pct DESC
LIMIT 10;

-- 7. Top 10 Best Selling Products
SELECT
    oi.product_id,
    COALESCE(ct.product_category_name_english, 'Uncategorized') AS category,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(AVG(oi.price), 2) AS avg_price,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation ct ON p.product_category_name = ct.product_category_name
GROUP BY oi.product_id, ct.product_category_name_english
ORDER BY total_revenue DESC
LIMIT 10;

-- 8. Sales Distribution by Price Range
SELECT
    CASE
        WHEN price < 50 THEN 'Under R$ 50'
        WHEN price BETWEEN 50 AND 99.99 THEN 'R$ 50 - R$ 100'
        WHEN price BETWEEN 100 AND 249.99 THEN 'R$ 100 - R$ 250'
        WHEN price BETWEEN 250 AND 499.99 THEN 'R$ 250 - R$ 500'
        ELSE 'R$ 500+'
    END AS price_tier,
    COUNT(*) AS units_sold,
    ROUND(SUM(price), 2) AS total_merchandise_value,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM order_items
GROUP BY 1
ORDER BY 1;

-- 9. Top 10 Customer States by Revenue
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS unique_customers,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue,
    ROUND(
        SUM(oi.price + oi.freight_value) * 100.0 / 
        (SELECT SUM(price + freight_value) FROM order_items), 2
    ) AS revenue_share_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;

-- 10. Seller Distribution by State
SELECT
    s.seller_state,
    COUNT(DISTINCT s.seller_id) AS total_sellers,
    COUNT(DISTINCT oi.order_id) AS orders_fulfilled,
    ROUND(SUM(oi.price), 2) AS total_sales,
    ROUND(COUNT(DISTINCT s.seller_id) * 100.0 / (SELECT COUNT(*) FROM sellers), 2) AS seller_share_pct
FROM sellers s
LEFT JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_state
ORDER BY total_sellers DESC
LIMIT 10;

-- 11. Intra-State vs Inter-State Shipping Performance
SELECT
    CASE 
        WHEN c.customer_state = s.seller_state THEN 'Same State (Intra-State)'
        ELSE 'Cross-State (Inter-State)'
    END AS delivery_type,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight,
    ROUND(
        AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400)::NUMERIC, 1
    ) AS avg_delivery_days
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN sellers s ON oi.seller_id = s.seller_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY 1;

-- 12. Customer Repeat Purchase Rate
WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_unique_id
)
SELECT
    CASE 
        WHEN order_count = 1 THEN '1 Order (One-Time)'
        WHEN order_count = 2 THEN '2 Orders (Repeat)'
        WHEN order_count = 3 THEN '3 Orders (Loyal)'
        ELSE '4+ Orders (VIP)'
    END AS customer_type,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM customer_orders
GROUP BY 1
ORDER BY 1;

-- 13. Top 10 Sellers by Revenue
SELECT
    s.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders_fulfilled,
    COUNT(oi.order_item_id) AS units_sold,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS total_revenue
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
GROUP BY s.seller_id, s.seller_city, s.seller_state
ORDER BY total_revenue DESC
LIMIT 10;

-- 14. Delivery Performance by State (Actual vs Estimated Delivery Days)
SELECT
    c.customer_state,
    COUNT(o.order_id) AS delivered_orders,
    ROUND(AVG(EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400)::NUMERIC, 1) AS avg_actual_days,
    ROUND(AVG(EXTRACT(EPOCH FROM (o.order_estimated_delivery_date - o.order_purchase_timestamp)) / 86400)::NUMERIC, 1) AS avg_estimated_days,
    ROUND(COUNT(*) FILTER (WHERE o.order_delivered_customer_date <= o.order_estimated_delivery_date) * 100.0 / COUNT(*), 2) AS on_time_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY delivered_orders DESC
LIMIT 10;

-- 15. Customer Review Score Breakdown
SELECT
    review_score,
    COUNT(*) AS review_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM reviews
GROUP BY review_score
ORDER BY review_score DESC;

-- 16. Impact of Delivery Speed on Customer Satisfaction
WITH delivery_speed AS (
    SELECT
        o.order_id,
        r.review_score,
        CASE
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date - INTERVAL '5 days' 
                THEN 'Delivered > 5 Days Early'
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                THEN 'Delivered On-Time (0-5d Early)'
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date + INTERVAL '5 days' 
                THEN 'Delayed 1-5 Days'
            ELSE 'Delayed > 5 Days'
        END AS delivery_status
    FROM orders o
    JOIN reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT
    delivery_status,
    COUNT(*) AS total_orders,
    ROUND(AVG(review_score), 2) AS avg_review_score,
    ROUND(COUNT(*) FILTER (WHERE review_score = 5) * 100.0 / COUNT(*), 2) AS five_star_pct,
    ROUND(COUNT(*) FILTER (WHERE review_score = 1) * 100.0 / COUNT(*), 2) AS one_star_pct
FROM delivery_speed
GROUP BY delivery_status
ORDER BY delivery_status;
