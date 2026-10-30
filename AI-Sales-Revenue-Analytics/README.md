# RetailX: Customer Segmentation with Ground-Truth Validation

Synthetic RetailX sales pipeline. Customers belong to five latent behavior types (Bargain Hunters, Loyal Regulars, Big Spenders, Occasional Shoppers, Impulse Buyers) that actually drive order frequency, timing, basket size, and discount usage. The pipeline generates reproducible synthetic data, cleans it, builds per-customer features, runs K-Means clustering (k=2..8), validates clusters against the held-out latent ground truth, and compares algorithms plus a supervised ceiling.

## Pipeline

1. Generate reproducible synthetic data (writes to `v2/data/raw/`):

```powershell
python src/generate_data.py --out-dir v2/data/raw
```

2. Run cleaning, features, clustering, validation, and reporting (writes CSVs to `v2/reports/`):

```powershell
python v2/run_v2.py
```

## Quick start

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the full pipeline:

```powershell
python src/generate_data.py --out-dir v2/data/raw
python v2/run_v2.py
```

## Repository structure

```
AI-Sales-Revenue-Analytics/
├── archive/                 # superseded generator (generate_data_old.py)
├── src/
│   ├── __init__.py
│   ├── config.py            # SEED and project paths
│   └── generate_data.py     # synthetic generator with latent-type-driven behavior
├── v2/
│   ├── run_v2.py            # full cleaning/features/clustering/validation pipeline
│   ├── data/raw/            # generated synthetic data (gitignored, reproducible)
│   └── reports/             # cleaning_log.csv, k_selection.csv, segment_profile_k5.csv, customer_labels_k5.csv, ...
├── _cleanup_trash/          # superseded files moved out of the active tree
├── requirements.txt         # pandas, numpy, scikit-learn, scipy (pinned)
├── README.md
└── .gitignore
```

## Verified metrics (single reproducible run, seed 42)

- Raw rows before dedup: 37,749; rows after dedup: 37,562; PCT_RETAINED: 99.5046%
- Duplicates dropped: 187; corrupt discounts fixed: 75
- Clustering features: Num_Orders, Avg_Order_Value, Recency_Days, Avg_Items_Per_Order
- K selection (k=2..8): best silhouette at k=2
- K=5 vs latent ground truth: ARI_GT 0.3563, NMI_GT 0.4100
- Supervised ceiling (RandomForest, 5-fold): accuracy 0.7541, macro F1 0.7553

## Git handling

- Tracked: `src/`, `v2/run_v2.py`, `v2/reports/`, `archive/`, `requirements.txt`, `README.md`, `.gitignore`
- Gitignored (not committed): `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `mlflow.db`, `mlruns/`, `v2/data/raw/`, `_cleanup_trash/`, `venv/`

Generated data under `v2/data/raw/` is reproducible via `src/generate_data.py` and is deliberately not committed.

## Notes

- Latent customer types are ground truth for evaluation only; they are never used as clustering features (no data leakage).
- A fresh-clone reproducibility test could not be completed because the environment has no network access to PyPI (`pip install` times out). Do not claim fresh-clone reproducibility without verification.
