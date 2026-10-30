import os
from pathlib import Path

# Central configuration for RetailX project
SEED = 42

# Project root (retailx/ if exists, else repo root)
def get_project_root():
    # Try to find retailx directory
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == 'retailx':
            return parent
    # Fallback to repo root containing this file
    return Path(__file__).resolve().parents[2]

PROJECT_ROOT = get_project_root()
REPO_ROOT = PROJECT_ROOT.parent if PROJECT_ROOT.name == 'retailx' else PROJECT_ROOT

# Data paths
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
RAW_DATA_PATH = RAW_DATA_DIR / 'sales_data.csv'
CLEANED_DATA_PATH = PROCESSED_DATA_DIR / 'cleaned_sales_data.csv'
CUSTOMER_FEATURES_PATH = PROCESSED_DATA_DIR / 'customer_features.csv'
MONTHLY_SALES_PATH = PROCESSED_DATA_DIR / 'monthly_sales.csv'

# Reports paths
REPORTS_DIR = PROJECT_ROOT / 'reports'
FIGURES_DIR = REPORTS_DIR / 'figures'
CLEANING_LOG_PATH = REPORTS_DIR / 'cleaning_log.csv'
FEATURE_DECISIONS_PATH = REPORTS_DIR / 'feature_decisions.md'
K_SELECTION_PATH = REPORTS_DIR / 'k_selection.csv'
SEGMENT_PROFILE_PATH = REPORTS_DIR / 'segment_profile.csv'
SEGMENT_TESTS_PATH = REPORTS_DIR / 'segment_tests.csv'
RECOMMENDATIONS_PATH = REPORTS_DIR / 'recommendations.md'
BUSINESS_FINDINGS_PATH = REPORTS_DIR / 'business_findings.md'
RESULTS_SUMMARY_PATH = PROJECT_ROOT / 'RESULTS_SUMMARY.md'

# Models paths
MODELS_DIR = PROJECT_ROOT / 'models'
if not MODELS_DIR.exists():
    MODELS_DIR = REPO_ROOT / 'models'
SCALER_PATH = MODELS_DIR / 'scaler.pkl'
KMEANS_MODEL_PATH = MODELS_DIR / 'customer_kmeans.pkl'
FORECAST_MODEL_PATH = MODELS_DIR / 'sales_forecasting_model.pkl'

# SQL paths
SQL_DIR = PROJECT_ROOT / 'sql'
if not SQL_DIR.exists():
    SQL_DIR = REPO_ROOT / 'sql'

# Dashboard paths
DASHBOARD_DIR = PROJECT_ROOT / 'dashboard'
DASHBOARD_DATA_DIR = DASHBOARD_DIR / 'data'

# Snapshot date for recency calculation (fixed, not today's date)
# Will be computed from data as max(order_date) + 1 day
SNAPSHOT_DATE = None
