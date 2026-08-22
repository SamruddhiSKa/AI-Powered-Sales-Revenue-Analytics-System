# Power BI Dashboard Build Guide

The `.pbix` file must be created in Power BI Desktop. The project is prepared with PostgreSQL tables, CSV outputs, and DAX measures.

## 1. Connect the data

Use **Get Data > PostgreSQL database** and connect to the database configured in `.env`. Import or DirectQuery these tables:

- `customers`
- `products`
- `orders`
- `order_details`

Also import `outputs/insights/customer_clusters.csv` and `outputs/predictions/monthly_sales_forecast.csv`.

## 2. Relationships

Create these single-direction relationships:

- `customers[customer_id]` 1-to-many `orders[customer_id]`
- `orders[order_id]` 1-to-many `order_details[order_id]`
- `products[product_id]` 1-to-many `order_details[product_id]`

Create a calendar table:

```DAX
Dates = CALENDAR(MIN(orders[order_date]), MAX(orders[order_date]))
```

Add calculated columns:

```DAX
Year = YEAR(Dates[Date])
Month Number = MONTH(Dates[Date])
Month = FORMAT(Dates[Date], "MMM")
Year Month = FORMAT(Dates[Date], "YYYY-MM")
```

Mark `Dates` as the date table and relate `Dates[Date]` to `orders[order_date]`.

## 3. Report pages

### Executive Overview

KPI cards: Total Sales, Total Profit, Total Orders, Total Customers, Average Order Value, Profit Margin.

Charts: monthly sales and profit lines, revenue by category, revenue by region, and top 10 products. Add slicers for date, region, category, segment, and sales channel.

### Sales and Product Analysis

Use a matrix with product, sales, profit, quantity, and margin. Add conditional formatting to margin and profit. Add a scatter plot with discount on the x-axis, profit on the y-axis, and sales as bubble size.

### Customer Analytics

Show customer count, repeat customer count, customer revenue distribution, cluster distribution, top customers, and a table of segment revenue/profit.

### Regional Analytics

Use a drill-down hierarchy of Region > State > City. Display sales, profit, and margin by geography.

### AI Forecasting

Use the forecast output table with a line chart for actual and predicted sales. Clearly label predictions and show MAE, RMSE, and R-squared from `outputs/insights/forecast_metrics.csv`.

## 4. Design principles

Use a restrained business palette, consistent number formatting, visible filter context, and titles that state the business question. Predictions must be visually distinct from actual values and should not be presented as guarantees.
