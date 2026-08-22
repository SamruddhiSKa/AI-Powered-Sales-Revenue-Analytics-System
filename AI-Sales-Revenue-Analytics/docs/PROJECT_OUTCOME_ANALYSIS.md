 # RetailX Sales Analytics Project Outcome Analysis

## Overall Summary

Built an end-to-end sales and revenue analytics system covering synthetic data generation, data cleaning, relational database design, SQL analytics, Python EDA, customer segmentation, sales forecasting, and Power BI preparation. The system analyzes 32,340 raw transaction-detail rows representing 20,000 orders, 2,999 customers, 500 products, and 48 months of sales history. The cleaned dataset reports $11.21M revenue, $4.58M profit, a 40.88% profit margin, and a 99.03% repeat-customer rate. The strongest achievement is integrating the complete analytics lifecycle into one reproducible project; forecasting should be presented as a baseline because both evaluated models produced negative R-squared values.

## Complete Architecture

| Stage | What you built | Problem solved | Inputs and outputs | Technologies | Evidence |
|---|---|---|---|---|---|
| Data generation | Reproducible fictional retail dataset with customers, products, orders, geography, sales, profit, missing values, duplicates, and outliers | Created realistic data for an end-to-end portfolio project | Output: raw denormalized CSV | Python, NumPy, Pandas | `src/data_generator.py` |
| Data cleaning | Missing-value treatment, duplicate removal, validation, discount correction, profit recalculation, and category standardization | Produced reliable analytical data | Raw CSV to cleaned CSV | Pandas, NumPy | `src/data_cleaning.py` |
| SQL database | Normalized customer, product, order, and order-detail tables with keys and indexes | Reduced duplicated master data and enforced relational structure | Cleaned data to relational schema | PostgreSQL/MySQL SQL | `sql/database_schema.sql` |
| SQL analytics | KPI, ranking, monthly, customer, product, margin, and growth queries | Enabled reusable business analysis | Relational tables to result sets | SQL, CTEs, window functions | `sql/analytical_queries.sql` |
| Python EDA | KPI summaries, trends, product/category/region comparisons, customer distribution, and discount-profit analysis | Converted transactions into interpretable findings | Cleaned CSV to figures and summaries | Pandas, Matplotlib, Seaborn | `src/eda.py` |
| Feature engineering | Customer spend, order, profit, recency, frequency, and CLV-proxy features plus monthly aggregates | Created modeling-ready data | Cleaned data to feature CSVs | Pandas | `src/feature_engineering.py` |
| Segmentation | K-Means clustering on six standardized customer features | Identified behaviorally distinct customer groups | Customer features to four clusters and model artifact | Scikit-learn, Joblib | `src/customer_segmentation.py` |
| Forecasting | Linear Regression and Random Forest comparison with chronological validation | Estimated monthly sales and measured predictive performance | Monthly sales to metrics and predictions | Scikit-learn, Joblib | `src/sales_forecasting.py` |
| Power BI | Five-page dashboard design, relationships, slicers, KPI cards, and DAX measures | Prepared analysis for management decision support | SQL, segmentation, and forecast outputs to BI specification | Power BI, DAX | `powerbi/POWERBI_BUILD_GUIDE.md`, `powerbi/dax_measures.md` |

## Project Scale

- **32,340** raw transaction-detail rows
- **32,181** cleaned rows
- **20,000** distinct orders
- **2,999** customers
- **500** products
- **5** categories, **4** regions, **6** states, and **6** cities
- **26** raw columns and **28** cleaned columns
- **48 months** from **2020-01-01 to 2023-12-30**
- Raw CSV size: approximately **6.00 MB**; cleaned CSV size: approximately **6.99 MB**

## Data Cleaning Results

| Measure | Result |
|---|---:|
| Duplicate rows removed | **159** |
| Records retained | **99.51%** |
| Missing values before cleaning | **966** |
| Missing values after cleaning | **0** |
| Missing customer ages | **483** |
| Missing customer genders | **483** |
| Extreme discounts above 80% | **65** |
| Extreme discounts after cleaning | **0** |
| Invalid quantity rows removed | **0** |
| Negative-sales rows removed | **0** |
| Profit formula consistency after cleaning | **100%** |

The pipeline added `Calculated_Profit` and `Profit_Margin`. The repository supports missing age and gender claims. Although the generator attempts to create missing unit prices, the final denormalization restores product prices, so missing unit-price rows should not be reported.

## Observed Sales Results

| KPI | Result |
|---|---:|
| Total revenue | **$11,208,407.24** |
| Total profit | **$4,582,262.02** |
| Profit margin | **40.88%** |
| Total orders | **20,000** |
| Customers | **2,999** |
| Average order value | **$560.42** |
| Average orders per customer | **6.67** |
| Repeat customers | **2,970** |
| Repeat-customer rate | **99.03%** |
| Maximum orders by one customer | **17** |
| Returned orders | **408** |
| Returned-order rate | **2.04%** |

### Category Performance

| Category | Revenue | Revenue share | Margin |
|---|---:|---:|---:|
| Electronics | $3,233,250.74 | 28.85% | 41.22% |
| Clothing | $2,607,396.32 | 23.26% | 39.95% |
| Furniture | $2,201,773.10 | 19.64% | 41.78% |
| Home & Kitchen | $1,803,051.07 | 16.09% | 41.52% |
| Office Supplies | $1,362,936.01 | 12.16% | 39.57% |

Electronics leads revenue. Furniture has the highest category margin, while Office Supplies has the lowest.

### Regional Performance

| Region | Revenue | Revenue share | Margin |
|---|---:|---:|---:|
| Midwest | $2,849,258.86 | 25.42% | 40.77% |
| South | $2,837,688.30 | 25.32% | 40.81% |
| West | $2,800,965.03 | 24.99% | 40.97% |
| East | $2,720,495.05 | 24.27% | 40.99% |

Regional revenue is balanced; the highest region exceeds the lowest by approximately 4.73%.

### Concentration and Trends

- The top product generated **$68,839.16**, or **0.61%** of revenue.
- The top 10 products generated approximately **4.88%** of revenue.
- The top customer generated **$12,982.97**, or **0.12%** of revenue.
- The top five customers generated approximately **0.55%** of revenue.
- Highest-sales month: **October 2022**, with **$264,652.53**.
- First observed month: **$233,502.19**; last observed month: **$218,375.79**.
- First-to-last monthly comparison: **6.48% lower**.

The first-to-last comparison does not prove a sustained decline; year-over-year or formal trend analysis would be required.

## SQL Achievements

- **4 normalized tables:** `customers`, `products`, `orders`, and `order_details`
- **3 foreign-key relationships** and **3 indexes**
- **10 analytical query blocks**
- Aggregation by product, customer, category, region, and month
- Average order value and top-customer analysis
- Top-10 products and top-five products within each category
- Month-over-month growth using `LAG`
- High-sales, low-margin product screening
- CTE and window-function usage

No query execution plans or benchmarks are included, so database performance improvements cannot be quantified.

## Python EDA Achievements

The EDA process generated **7 figures** and **7 insight CSVs** covering KPI summaries, monthly trends, top products, category performance, discount-profit relationships, customer spend distribution, and regional performance. The main findings are Electronics leadership, balanced regions, high repeat purchasing, low product/customer concentration, and the October 2022 sales peak. Formal correlation coefficients, significance tests, and additional outlier counts are not included.

## Machine Learning Results

### Customer Segmentation

- Unsupervised **K-Means** model
- **2,999 customers**, **6 behavioral features**, **4 clusters**
- Features: total spend, total orders, average order value, total profit, recency, and frequency
- Standardized with `StandardScaler`
- Candidate values of `k`: **2 through 8**

| Cluster | Customers | Customer share | Revenue share | Profit share | Avg. spend | Avg. orders | Avg. order value |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 698 | 23.27% | 38.01% | 38.09% | $6,103.84 | 10.00 | $369.24 |
| 1 | 1,030 | 34.34% | 23.90% | 23.80% | $2,600.55 | 6.21 | $277.38 |
| 2 | 479 | 15.97% | 7.83% | 7.76% | $1,831.87 | 3.63 | $322.21 |
| 3 | 792 | 26.41% | 30.26% | 30.35% | $4,282.70 | 6.16 | $439.77 |

The highest-value segment represents 23.27% of customers but contributes 38.01% of revenue. Silhouette scores, Davies-Bouldin scores, stability tests, and formal business labels are not currently included.

### Sales Forecasting

- **48** historical monthly periods; **46** usable after lag creation
- **34-month training / 12-month test** split
- Features: time index, one-month lag, and two-month lag
- Models: Linear Regression and Random Forest with 200 estimators

| Model | MAE | RMSE | R-squared |
|---|---:|---:|---:|
| Linear Regression | $12,783.38 | $15,090.72 | -0.5092 |
| Random Forest | $17,672.36 | $19,670.61 | -1.5643 |

Linear Regression was selected by RMSE and generated **12 predictions**. Both models have negative R-squared values, so this is a forecasting baseline rather than a production-ready model. Aggregate predicted test-period sales were $2,828,379.55 versus actual sales of $2,779,767.79, an overprediction of approximately 1.75%.

## Power BI Contribution

The project contains a Power BI build specification, not a completed `.pbix` file.

- **5 planned pages:** Executive Overview, Sales and Product Analysis, Customer Analytics, Regional Analytics, and AI Forecasting
- **12 documented DAX measures**
- KPI cards for sales, profit, orders, customers, average order value, and profit margin
- Slicers for date, region, category, segment, and sales channel
- Calendar table and relational model
- Forecast and segmentation outputs prepared for reporting

Do not claim a completed dashboard, deployed report, actual visualization count, refresh performance, or user adoption because those artifacts are not present.

## Quantified Achievement Table

| Stage | My Achievement | Scale | Result | Business/Technical Impact | Evidence |
|---|---|---:|---|---|---|
| Data Cleaning | Built reproducible cleaning and validation pipeline | 32,340 raw rows | 159 duplicates removed; 966 missing values resolved; 99.51% retained | Improved analytical reliability | `src/data_cleaning.py` |
| SQL Database | Designed normalized relational model | 4 tables, 3 indexes, 3 FK relationships | Customer, product, order, and detail grains separated | Reduced duplication and improved structure | `sql/database_schema.sql` |
| SQL Analytics | Authored reusable business queries | 10 query blocks | Rankings, CTEs, window functions, MoM growth, and margin analysis | Enabled repeatable analysis | `sql/analytical_queries.sql` |
| Python EDA | Automated business-focused exploratory analysis | 7 figures and 7 CSVs | KPI, trend, category, region, product, customer, and discount analysis | Converted transactions into insight outputs | `src/eda.py` |
| Machine Learning | Compared forecasting models with chronological validation | 46 usable months; 34/12 split | Best RMSE: $15,090.72; R-squared: -0.5092 | Established an auditable baseline | `outputs/insights/forecast_metrics.csv` |
| Segmentation | Created customer behavioral groups | 2,999 customers; 6 features; 4 clusters | Leading cluster: 23.27% of customers and 38.01% of revenue | Supports differentiated customer strategies | `outputs/insights/cluster_summary.csv` |
| Power BI | Prepared management dashboard specification | 5 pages; 12 DAX measures | Executive, product, customer, regional, and forecast views | Defines a decision-support layer | `powerbi/POWERBI_BUILD_GUIDE.md` |
| Overall System | Connected the full analytics lifecycle | $11.21M revenue; 20,000 orders | Raw data through ML and BI preparation | Demonstrates end-to-end ownership | `README.md` |

## My Project in Numbers

**32,340** raw rows | **32,181** cleaned rows | **20,000** orders | **2,999** customers | **500** products | **48 months** | **$11.21M** revenue | **$4.58M** profit | **40.88%** margin | **99.03%** repeat customers | **159** duplicates removed | **966** missing values resolved | **99.51%** retention | **10** SQL query blocks | **7** EDA figures | **4** customer segments | **6** segmentation features | **12** forecast predictions | **5** planned Power BI pages | **12** DAX measures

## Top 10 Achievements

1. Built a complete raw-data-to-dashboard analytics architecture.
2. Processed 32,340 transaction-detail rows into a validated dataset.
3. Removed 159 duplicates and resolved 966 missing values while retaining 99.51% of records.
4. Designed a normalized four-table relational database model.
5. Implemented SQL using CTEs, window functions, rankings, and month-over-month analysis.
6. Created a six-feature K-Means segmentation model for 2,999 customers.
7. Identified a segment representing 23.27% of customers but 38.01% of revenue.
8. Used chronological validation with a final 12-month forecasting holdout.
9. Compared Linear Regression and Random Forest using MAE, RMSE, and R-squared.
10. Prepared a five-page Power BI design with 12 DAX measures.

## Resume-Quality Statements

- Built an end-to-end sales analytics pipeline processing **32,340 transaction-detail rows**, integrating Python, SQL, machine learning, and Power BI preparation.
- Cleaned and validated retail data by removing **159 duplicates**, resolving **966 missing values**, capping **65 extreme discounts**, and retaining **99.51%** of source rows.
- Designed a normalized SQL schema with **4 relational tables**, foreign-key constraints, and **3 indexes** for customer, product, order, and order-detail analysis.
- Authored **10 analytical SQL query blocks** using CTEs, window functions, rankings, month-over-month growth, and product-margin analysis.
- Engineered behavioral features for **2,999 customers** using spend, orders, order value, profit, recency, and frequency.
- Developed a K-Means model using **6 standardized features**, identifying **4 customer segments**.
- Identified a high-value segment representing **23.27% of customers but 38.01% of revenue**, supporting targeted retention and upselling strategies.
- Built monthly sales forecasting with a chronological **34-month training and 12-month test split**.
- Prepared a five-page Power BI dashboard design with **12 DAX measures**.

## Observed Results Versus Potential Business Value

### Observed results

The cleaned synthetic dataset contains $11.21M revenue, $4.58M profit, a 40.88% margin, a 99.03% repeat-customer rate, four customer clusters, a 2.04% returned-order rate, balanced regional performance, and Electronics as the leading revenue category.

### Potential business impact

The system could support prioritized retention, customer reactivation, upselling, cross-selling, product and margin reviews, regional comparison, monthly planning, and forecast monitoring. The project does not contain evidence that revenue increased, costs decreased, or campaigns produced actual financial outcomes. Those claims should not be made.

## What Would Make the Project More Impressive?

1. Add Pandera, Great Expectations, or pytest data-quality checks and report duplicate, invalid-row, missingness, and test-pass rates.
2. Explicitly correct or quantify the sales outliers introduced by the generator and report their revenue impact.
3. Add completed, returned, cancelled, gross, and net sales KPIs, including return and cancellation rates.
4. Compare forecasting against seasonal-naive, moving-average, and mean baselines using MAE, RMSE, and MAPE.
5. Add seasonal lags, rolling averages, promotions, discounts, holidays, product mix, and channel mix, then report metric improvement.
6. Add silhouette score, Davies-Bouldin score, and cluster stability for quantitative segmentation validation.
7. Add cohort retention, month-1/month-3/month-6 retention, and customer lifecycle analysis.
8. Replace the current profit-equals-CLV proxy with a forward-looking CLV model and report CLV by segment.
9. Capture `EXPLAIN ANALYZE` before and after indexes and report query runtime reduction.
10. Build and save the actual `.pbix` file, then report pages, visuals, slicers, refresh time, and screenshots.
11. Add orchestration, package versions, random seed, timestamps, row counts, and a run manifest.
12. Add correlations, confidence intervals, significance tests, and robust outlier diagnostics.

## Overall Achievement

You built an end-to-end sales and revenue analytics system covering 32,340 raw transaction-detail rows, 20,000 orders, 2,999 customers, 500 products, and 48 months of synthetic retail data. The system combines Python data engineering and EDA, normalized SQL modeling and analytics, K-Means customer segmentation, sales forecasting, and a five-page Power BI design. It reports $11.21M revenue, $4.58M profit, a 40.88% margin, and a 99.03% repeat-customer rate, while identifying four economically distinct customer segments. Its strongest achievement is demonstrating complete analytics ownership from raw data through decision-ready insights, with forecasting accurately framed as a baseline requiring further improvement.
