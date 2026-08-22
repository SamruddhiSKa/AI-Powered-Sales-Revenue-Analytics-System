-- Analytical SQL queries for RetailX Analytics

-- Basic KPIs
-- Total Sales
SELECT SUM(sales) AS total_sales FROM order_details;

-- Total Profit
SELECT SUM(profit) AS total_profit FROM order_details;

-- Total Orders
SELECT COUNT(DISTINCT order_id) AS total_orders FROM orders;

-- Average Order Value
SELECT AVG(order_tot) FROM (
  SELECT order_id, SUM(sales) as order_tot FROM order_details GROUP BY order_id
) t;

-- Top 10 products by sales
SELECT p.product_id, p.product_name, SUM(od.sales) AS product_sales
FROM order_details od
JOIN products p ON od.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY product_sales DESC
LIMIT 10;

-- Monthly sales (example using order_date from orders)
SELECT DATE_TRUNC('month', o.order_date) AS month, SUM(od.sales) AS monthly_sales
FROM orders o
JOIN order_details od ON o.order_id = od.order_id
GROUP BY month
ORDER BY month;

-- Top customers by revenue
SELECT c.customer_id, c.customer_name, SUM(od.sales) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_details od ON o.order_id = od.order_id
GROUP BY c.customer_id, c.customer_name
ORDER BY revenue DESC
LIMIT 20;

-- Advanced queries
-- Top 5 products in each category
WITH prod_sales AS (
  SELECT p.category, p.product_id, p.product_name, SUM(od.sales) AS sales
  FROM order_details od
  JOIN products p ON od.product_id = p.product_id
  GROUP BY p.category, p.product_id, p.product_name
)
SELECT category, product_id, product_name, sales
FROM (
  SELECT *, RANK() OVER (PARTITION BY category ORDER BY sales DESC) as rnk FROM prod_sales
) t
WHERE rnk <= 5
ORDER BY category, sales DESC;

-- Month-over-month sales growth
WITH monthly AS (
  SELECT DATE_TRUNC('month', o.order_date) AS month, SUM(od.sales) AS monthly_sales
  FROM orders o JOIN order_details od ON o.order_id = od.order_id
  GROUP BY month
)
SELECT month,
       monthly_sales,
       LAG(monthly_sales) OVER (ORDER BY month) AS prev_month,
       (monthly_sales - LAG(monthly_sales) OVER (ORDER BY month)) / NULLIF(LAG(monthly_sales) OVER (ORDER BY month),0) AS mom_growth
FROM monthly
ORDER BY month;

-- Products with high sales but low profit margin
SELECT p.product_id, p.product_name, SUM(od.sales) AS sales, SUM(od.profit) AS profit, SUM(od.profit)/NULLIF(SUM(od.sales),0) AS profit_margin
FROM order_details od JOIN products p ON od.product_id = p.product_id
GROUP BY p.product_id, p.product_name
HAVING SUM(od.sales) > 10000 AND SUM(od.profit)/NULLIF(SUM(od.sales),0) < 0.05
ORDER BY sales DESC;
