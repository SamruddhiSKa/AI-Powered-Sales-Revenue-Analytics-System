"""
Customer segmentation using K-Means.
Loads data/processed/customer_features.csv (or generates features if missing), scales features, finds k via elbow method, fits KMeans, and saves model and summaries.
"""
import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import joblib

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
FEATURES_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'customer_features.csv')
CLEAN_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'cleaned_sales_data.csv')
OUT_DIR = os.path.join(PROJ_ROOT, 'outputs')
MODELS_DIR = os.path.join(PROJ_ROOT, 'models')


def ensure_features():
    if not os.path.exists(FEATURES_PATH):
        from feature_engineering import create_customer_features
        df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])
        cust = create_customer_features(df)
        os.makedirs(os.path.dirname(FEATURES_PATH), exist_ok=True)
        cust.to_csv(FEATURES_PATH, index=False)
    return pd.read_csv(FEATURES_PATH)


if __name__ == '__main__':
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = ensure_features()
    # Select features for clustering
    features = df[['Total_Spend','Total_Orders','Avg_Order_Value','Total_Profit','Recency_Days','Frequency']].fillna(0)

    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    # Determine k using elbow (up to 8)
    sse = []
    K = range(2,9)
    for k in K:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X)
        sse.append(km.inertia_)

    plt.figure()
    plt.plot(list(K), sse, '-o')
    plt.xlabel('k')
    plt.ylabel('SSE')
    plt.title('Elbow Method for K')
    elbow_path = os.path.join(OUT_DIR, 'figures', 'k_elbow.png')
    os.makedirs(os.path.dirname(elbow_path), exist_ok=True)
    plt.savefig(elbow_path)
    plt.close()

    # Choose k=4 as a reasonable default
    k = 4
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    df['Cluster'] = labels

    # Save cluster summary
    summary = df.groupby('Cluster').agg({
        'Customer_ID':'nunique',
        'Total_Spend':'mean',
        'Total_Orders':'mean',
        'Avg_Order_Value':'mean',
        'Total_Profit':'mean',
        'Recency_Days':'mean'
    }).rename(columns={'Customer_ID':'Num_Customers'})
    summary_path = os.path.join(OUT_DIR, 'insights', 'cluster_summary.csv')
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    summary.to_csv(summary_path)

    # Save labeled customers and model
    df.to_csv(os.path.join(OUT_DIR, 'insights', 'customer_clusters.csv'), index=False)
    joblib.dump({'scaler':scaler, 'kmeans':km}, os.path.join(MODELS_DIR, 'customer_kmeans.pkl'))

    print(f'Saved cluster plot to {elbow_path}, summary to {summary_path}, and model to models/customer_kmeans.pkl')
