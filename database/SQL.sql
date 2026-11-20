
-- ============================================
-- OLIST E-COMMERCE DATABASE
-- DATABASE: olist_ecommerce
-- ============================================

-- 1. CUSTOMERS
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_unique_id VARCHAR(50),
    customer_zip_code_prefix VARCHAR(5),
    customer_city VARCHAR(100),
    customer_state VARCHAR(5)
);

-- 2. PRODUCTS
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category_name VARCHAR(150),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

-- 3. SELLERS
CREATE TABLE sellers (
    seller_id VARCHAR(50) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(5),
    seller_city VARCHAR(100),
    seller_state VARCHAR(5)
);

-- 4. CATEGORY TRANSLATION
CREATE TABLE category_translation (
    product_category_name VARCHAR(150) PRIMARY KEY,
    product_category_name_english VARCHAR(150)
);

-- 5. GEOLOCATION
-- ZIP codes are not unique.
CREATE TABLE geolocation (
    geolocation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    geolocation_zip_code_prefix VARCHAR(5),
    geolocation_lat DOUBLE PRECISION,
    geolocation_lng DOUBLE PRECISION,
    geolocation_city VARCHAR(150),
    geolocation_state VARCHAR(5)
);

-- 6. ORDERS
CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_status VARCHAR(30),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    CONSTRAINT fk_orders_customers
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- 7. ORDER ITEMS
CREATE TABLE order_items (
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(12,2),
    freight_value NUMERIC(12,2),

    PRIMARY KEY (order_id, order_item_id),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    FOREIGN KEY (seller_id)
        REFERENCES sellers(seller_id)
);

-- 8. PAYMENTS
CREATE TABLE payments (
    order_id VARCHAR(50) NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type VARCHAR(50),
    payment_installments INTEGER,
    payment_value NUMERIC(12,2),

    PRIMARY KEY (order_id, payment_sequential),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

-- 9. REVIEWS
CREATE TABLE reviews (
    review_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,

    PRIMARY KEY (review_id, order_id),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    CONSTRAINT chk_review_score
        CHECK (review_score BETWEEN 1 AND 5)
);

-- ============================================
-- INDEXES FOR QUERY PERFORMANCE
-- ============================================

CREATE INDEX idx_orders_customer
ON orders(customer_id);

CREATE INDEX idx_orders_purchase_date
ON orders(order_purchase_timestamp);

CREATE INDEX idx_orders_status
ON orders(order_status);

CREATE INDEX idx_order_items_product
ON order_items(product_id);

CREATE INDEX idx_order_items_seller
ON order_items(seller_id);

CREATE INDEX idx_payments_type
ON payments(payment_type);

CREATE INDEX idx_reviews_score
ON reviews(review_score);

CREATE INDEX idx_geolocation_zip
ON geolocation(geolocation_zip_code_prefix);

-- ============================================
-- DATABASE DESIGN COMPLETED
-- =====================================


/*Verify your database*/
SELECT
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'
ORDER BY table_name;

/*verify the primary and foreign keys:*/

SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
ORDER BY tc.table_name, tc.constraint_type;







SELECT 'customers' AS table_name, COUNT(*) AS total_records FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL
SELECT 'category_translation', COUNT(*) FROM category_translation
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
 