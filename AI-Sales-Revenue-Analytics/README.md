# AI-Powered Sales & Revenue Analytics System

This repository contains a portfolio-ready analytics project for a fictional retail company, RetailX. It demonstrates the full pipeline: synthetic data generation, data cleaning, SQL database design, exploratory analysis, feature engineering, customer segmentation, sales forecasting, and Power BI dashboard preparation.

Quick start
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Generate synthetic data and run cleaning:

```powershell
python src/data_generator.py
python src/data_cleaning.py
```

4. Create features and run ML scripts:

```powershell
python src/feature_engineering.py
python src/customer_segmentation.py
python src/sales_forecasting.py
```

5. Generate EDA figures and KPI summaries:

```powershell
python src/eda.py
```

6. Load PostgreSQL (after creating `.env` from `.env.example`):

```powershell
python src/load_to_postgres.py
```

Project structure

```
AI-Sales-Revenue-Analytics/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── sql/
├── src/
├── models/
├── outputs/
├── powerbi/
├── requirements.txt
├── README.md
└── .gitignore
```

Useful scripts
- `src/data_generator.py` — generates realistic synthetic sales data (~10k–50k records).
- `src/data_cleaning.py` — cleans and validates the raw dataset.
- `src/load_to_postgres.py` — loads cleaned data into PostgreSQL (requires `.env` with credentials).
- `src/feature_engineering.py` — prepares customer- and time-level features.
- `src/customer_segmentation.py` — K-Means segmentation and cluster summaries.
- `src/sales_forecasting.py` — monthly sales forecasting (linear baseline and random forest).
- `src/eda.py` — business-focused figures and summary outputs.

Outputs
- `outputs/figures/` — monthly trends, category/region comparisons, discount analysis, and customer distribution.
- `outputs/insights/` — KPI, category, region, cluster, and forecast summaries.
- `outputs/predictions/` — actual versus predicted monthly sales.
- `models/` — K-Means and forecasting model artifacts.

Power BI
The data model, DAX measures, page layout, relationships, and visual recommendations are documented in `powerbi/dax_measures.md` and `powerbi/POWERBI_BUILD_GUIDE.md`. Power BI Desktop is required to save the final `.pbix` report.

Documentation
- `docs/PROJECT_DOCUMENTATION.md` — technical project documentation.
- `docs/INTERVIEW_PREPARATION.md` — concise explanations of technical and business decisions.
