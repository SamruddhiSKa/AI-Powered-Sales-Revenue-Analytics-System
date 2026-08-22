# Interview Preparation Notes

## SQL

**Why PostgreSQL?** It provides relational integrity, joins, constraints, indexes, and strong analytical SQL support.

**Why normalize the model?** Customers, products, orders, and order details have different grains. Normalization avoids duplicated master data and makes relationships explicit.

**Why use CTEs and window functions?** CTEs make multi-step analysis readable. Window functions calculate rankings and month-over-month comparisons without collapsing row-level context.

## Python and data quality

**How were missing values handled?** Age was median-imputed, missing gender was assigned `Unknown`, and rows missing essential pricing values were excluded because reliable imputation was not possible.

**How were outliers handled?** Extreme discounts were capped at a business-plausible threshold and profit was recalculated from unit price, cost, quantity, and discount. The raw data is retained to demonstrate the audit trail.

**Why Pandas?** It provides transparent, reproducible tabular transformations and integrates naturally with the visualization and ML stack.

## Machine learning

**Why K-Means?** Customer segment labels were unavailable, so unsupervised clustering was appropriate. Standardization prevents high-spend features from dominating distance calculations.

**How was k selected?** The elbow curve was reviewed and k=4 was chosen as an interpretable balance between segment detail and operational simplicity. Cluster profiles were inspected before assigning business meaning.

**Why chronological forecasting validation?** Future observations must not influence training. The final 12 months were held out as a realistic test period.

**Why MAE, RMSE, and R-squared?** MAE is easy to interpret, RMSE penalizes larger errors, and R-squared describes explained variance. No single metric is treated as sufficient.

## Power BI

**Measures versus calculated columns:** Measures are evaluated in filter context and are preferred for KPIs. Calculated columns are row-level values used for grouping or relationships.

**Dashboard design:** The report follows the management workflow: overview, product decisions, customer actions, regional diagnosis, and forecast context.

## Business discussion

The most useful findings should be read from the generated CSV summaries rather than assumed in advance. A strong recommendation connects a measured finding to an action, for example reviewing pricing and supplier cost when a category has high sales but weak margin.

## Limitations

The dataset is synthetic, the forecast uses a compact feature set, and the Power BI report requires manual assembly in Power BI Desktop. Results demonstrate a repeatable method rather than production-grade predictions.
