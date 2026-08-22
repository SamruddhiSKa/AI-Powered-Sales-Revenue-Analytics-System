DAX measures for Power BI dashboard

Total Sales = SUM(order_details[Sales])

Total Profit = SUM(order_details[Profit])

Total Orders = DISTINCTCOUNT(orders[Order_ID])

Total Customers = DISTINCTCOUNT(customers[Customer_ID])

Average Order Value = DIVIDE([Total Sales], [Total Orders])

Profit Margin = DIVIDE([Total Profit], [Total Sales])

Previous Month Sales = CALCULATE([Total Sales], PREVIOUSMONTH(dates[Date]))

Sales YTD = TOTALYTD([Total Sales], dates[Date])

Profit YTD = TOTALYTD([Total Profit], dates[Date])

Sales Growth % = DIVIDE([Total Sales] - [Previous Month Sales], [Previous Month Sales])

Customer Contribution % = DIVIDE([Total Sales], CALCULATE([Total Sales], ALL(customers)))

Average Discount = AVERAGE(order_details[Discount])

Notes:
- Create a `dates` calendar table and mark as date table.
- Use relationships: orders->order_details (Order_ID), customers->orders (Customer_ID), products->order_details (Product_ID).
