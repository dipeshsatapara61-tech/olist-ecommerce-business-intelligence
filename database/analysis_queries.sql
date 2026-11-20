SELECT DISTINCT
    p.product_category_name
FROM products p
LEFT JOIN category_translation ct
    ON p.product_category_name = ct.product_category_name
WHERE p.product_category_name IS NOT NULL
AND ct.product_category_name IS NULL
ORDER BY p.product_category_name;