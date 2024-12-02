SELECT 
    EXTRACT(MONTH FROM init_license_dt) AS month,
    business_type,
    COUNT(*) AS store_count
FROM 
    minato_restaurant
WHERE 
    EXTRACT(YEAR FROM init_license_dt) = 2022
GROUP BY 
    month, business_type
ORDER BY 
    month, business_type;