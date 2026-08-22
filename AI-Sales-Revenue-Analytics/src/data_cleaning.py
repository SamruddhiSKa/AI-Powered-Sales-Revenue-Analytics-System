"""
Data cleaning pipeline for RetailX synthetic dataset.
Saves cleaned file to data/processed/cleaned_sales_data.csv
"""
import pandas as pd
import numpy as np
import os

# Use project-relative absolute paths
proj_root = os.path.dirname(os.path.dirname(__file__))
RAW_PATH = os.path.join(proj_root, 'data', 'raw', 'sales_data.csv')
CLEAN_PATH = os.path.join(proj_root, 'data', 'processed', 'cleaned_sales_data.csv')

def load_data(path=RAW_PATH):
    df = pd.read_csv(path)
    return df


def _pick_best_column(df: pd.DataFrame, base_name: str) -> str | None:
    # Find columns that match base_name or start with base_name + '_'
    candidates = [c for c in df.columns if c == base_name or c.startswith(base_name + '_') or c.endswith('_' + base_name) or base_name in c]
    if not candidates:
        return None
    # Choose the candidate with the most non-null values
    best = max(candidates, key=lambda c: df[c].notna().sum())
    return best

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize common column names created during merges
    for base in ['Unit_Price','Cost','Sales','Profit','Quantity','Discount']:
        if base not in df.columns:
            best = _pick_best_column(df, base)
            if best:
                df = df.rename(columns={best: base})

    # Convert dates
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
    df['Ship_Date'] = pd.to_datetime(df['Ship_Date'], errors='coerce')

    # Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    print(f'Removed {before-after} duplicate rows')

    # Handle missing values: strategy per column
    # Customer_Age: fill with median
    if 'Customer_Age' in df.columns:
        df['Customer_Age'] = df['Customer_Age'].fillna(df['Customer_Age'].median())

    # Customer_Gender: fill with 'Unknown'
    if 'Customer_Gender' in df.columns:
        df['Customer_Gender'] = df['Customer_Gender'].fillna('Unknown')

    # Unit_Price: drop rows with missing unit price (can't impute reliably)
    if 'Unit_Price' in df.columns:
        df = df[~df['Unit_Price'].isna()]

    # Remove unrealistic quantities
    df = df[df['Quantity'] > 0]

    # Remove negative or zero sales where not expected
    df = df[df['Sales'] >= 0]

    # Handle outliers in Discount (>0.8 as extreme)
    df.loc[df['Discount'] > 0.8, 'Discount'] = 0.8

    # Recalculate Profit and Profit_Margin if inconsistent
    df['Calculated_Profit'] = (df['Unit_Price'] - df['Cost']) * df['Quantity'] * (1 - df['Discount'])
    # If existing Profit is NaN or differs significantly, replace
    mask = (df['Profit'].isna()) | (np.abs(df['Profit'] - df['Calculated_Profit']) > df['Calculated_Profit'].abs() * 0.2)
    df.loc[mask, 'Profit'] = df.loc[mask, 'Calculated_Profit']

    df['Profit_Margin'] = df['Profit'] / df['Sales'].replace(0, np.nan)
    df['Profit_Margin'] = df['Profit_Margin'].fillna(0)

    # Standardize categorical values
    df['Sales_Channel'] = df['Sales_Channel'].str.title()
    df['Payment_Mode'] = df['Payment_Mode'].str.title()
    df['Order_Status'] = df['Order_Status'].str.title()

    # Final sanity checks
    df = df.dropna(subset=['Order_ID','Customer_ID','Product_ID','Order_Date'])

    return df

if __name__ == '__main__':
    df = load_data()
    cleaned = clean_data(df)
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    cleaned.to_csv(CLEAN_PATH, index=False)
    print(f'Saved cleaned data to {CLEAN_PATH} with {len(cleaned)} rows')
