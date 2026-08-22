"""
Feature engineering utilities for RetailX project.
Generates:
- customer-level features CSV
- monthly aggregated sales CSV
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEAN_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'cleaned_sales_data.csv')
OUT_DIR = os.path.join(PROJ_ROOT, 'data', 'processed')


def create_customer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Customer-level aggregation
    cust = df.groupby('Customer_ID').agg(
        Total_Spend=pd.NamedAgg(column='Sales', aggfunc='sum'),
        Total_Orders=pd.NamedAgg(column='Order_ID', aggfunc=lambda x: x.nunique()),
        Avg_Order_Value=pd.NamedAgg(column='Sales', aggfunc='mean'),
        Total_Profit=pd.NamedAgg(column='Profit', aggfunc='sum'),
        Total_Quantity=pd.NamedAgg(column='Quantity', aggfunc='sum'),
        First_Purchase=pd.NamedAgg(column='Order_Date', aggfunc='min'),
        Last_Purchase=pd.NamedAgg(column='Order_Date', aggfunc='max')
    ).reset_index()

    cust['Recency_Days'] = (pd.to_datetime(df['Order_Date'].max()) - pd.to_datetime(cust['Last_Purchase'])).dt.days
    cust['Frequency'] = cust['Total_Orders'] / ((pd.to_datetime(df['Order_Date'].max()) - pd.to_datetime(cust['First_Purchase'])).dt.days.replace(0,1))
    cust['CLV'] = cust['Total_Profit'] * 1.0  # simple proxy
    return cust


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    monthly = df.groupby(pd.Grouper(key='Order_Date', freq='ME')).agg(Monthly_Sales=('Sales','sum'), Monthly_Profit=('Profit','sum')).reset_index()
    monthly['Year'] = monthly['Order_Date'].dt.year
    monthly['Month'] = monthly['Order_Date'].dt.month
    monthly['Month_Start'] = monthly['Order_Date'].dt.to_period('M').dt.to_timestamp()
    return monthly


if __name__ == '__main__':
    if not os.path.exists(CLEAN_PATH):
        raise SystemExit('Cleaned data not found. Run data_cleaning first.')
    df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])
    os.makedirs(OUT_DIR, exist_ok=True)

    cust_features = create_customer_features(df)
    cust_features.to_csv(os.path.join(OUT_DIR, 'customer_features.csv'), index=False)
    print('Saved customer features to data/processed/customer_features.csv')

    monthly = create_time_features(df)
    monthly.to_csv(os.path.join(OUT_DIR, 'monthly_sales.csv'), index=False)
    print('Saved monthly sales to data/processed/monthly_sales.csv')
