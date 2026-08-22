# Project Documentation

## 1. Problem Statement
RetailX wants a comprehensive analytics system to understand sales, customers, products, and forecast demand.

## 2. Objectives
- Generate a realistic retail dataset
- Clean and validate data
- Store in a relational database
- Perform SQL analytics
- Build EDA and ML models for segmentation and forecasting
- Create Power BI dashboards and DAX measures

## 3. Dataset
The synthetic dataset includes order, customer, product, geographic and financial fields. It contains missing values, duplicates, and intentional outliers to demonstrate cleaning.

## 4. Data Cleaning
See `src/data_cleaning.py` for cleaning logic: missing value imputation, duplicate removal, recalculation of profit, and standardization of categories.

## 5. Database Design
See `sql/database_schema.sql` for normalized schema: `customers`, `products`, `orders`, `order_details` and useful indexes.

## 6. SQL Analysis
See `sql/analytical_queries.sql` for basic and advanced analytical queries (window functions, CTEs, ranking, MoM growth).

## 7. EDA
Run `python src/eda.py` to generate figures and summary CSVs saved under `outputs/`.

## 8. Feature Engineering
`src/feature_engineering.py` creates customer-level features and monthly aggregates used for ML.

## 9. Customer Segmentation
`src/customer_segmentation.py` runs K-Means on scaled customer features, saves model to `models/customer_kmeans.pkl`, and outputs cluster summaries.

## 10. Sales Forecasting
`src/sales_forecasting.py` builds baseline linear and RandomForest models on monthly data, saves the best model and forecast outputs.

## 11. Power BI Dashboard
Place `AI-Sales-Revenue-Analytics/powerbi/Sales_Revenue_Analytics.pbix` here (placeholder). Use `powerbi/dax_measures.md` for DAX.

## 12. Results
Key outputs are in `outputs/insights`, `outputs/figures`, and `models/`.

## 13. Limitations
- Synthetic data; results illustrate techniques, not business truth.
- Forecasting uses simple features; production models require richer signals.

## 14. Future Scope
- Add cohort analysis, CLTV modeling, uplift tests, and more advanced time-series models (Prophet, LightGBM with lag features).
