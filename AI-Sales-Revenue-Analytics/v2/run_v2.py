import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
import numpy as np
import pandas as pd
from datetime import timedelta

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score, normalized_mutual_info_score, confusion_matrix, accuracy_score, f1_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from scipy.stats import kruskal

RAW = 'v2/data/raw/sales_data.csv'
LABELS = 'v2/data/raw/customer_latent_types.csv'
OUTDIR = 'v2/reports'
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(RAW, encoding='utf-8')
labels = pd.read_csv(LABELS, encoding='utf-8')
print('LOADED', df.shape)
rows_before_dedup = len(df)

# STEP A: CLEANING
print('\n--- CLEANING ---')
print('RAW_ROWS_BEFORE_DEDUP', rows_before_dedup)
missing_before = df.isna().sum()
print(missing_before.to_string())
missing_before.to_csv(os.path.join(OUTDIR, 'missing_before.csv'))

cleaning_log = []
rows_in = rows_before_dedup

dup_count = int(df.duplicated().sum())
rows_out = rows_in - dup_count
df = df.drop_duplicates()
cleaning_log.append({'step': 'drop_exact_duplicates', 'rows_in': rows_in, 'rows_out': rows_out, 'count_affected': dup_count})
print('ROWS_AFTER_DEDUP', rows_out)
print('DUPLICATES_DROPPED', dup_count)
rows_in = rows_out

age_missing_before = int(df['Customer_Age'].isna().sum())
gender_missing_before = int(df['Customer_Gender'].isna().sum())
df['Customer_Age'] = df['Customer_Age'].fillna(df['Customer_Age'].median())
df['Customer_Gender'] = df['Customer_Gender'].fillna('Unknown')
cleaning_log.append({'step': 'impute_customer_age_gender', 'rows_in': rows_in, 'rows_out': rows_in, 'count_affected': age_missing_before + gender_missing_before})

unit_price_missing_before = int(df['Unit_Price'].isna().sum())
for pid, g in df.groupby('Product_ID'):
    med = g['Unit_Price'].median()
    if pd.notna(med):
        df.loc[(df['Product_ID'] == pid) & (df['Unit_Price'].isna()), 'Unit_Price'] = med
unit_price_recovered = unit_price_missing_before - int(df['Unit_Price'].isna().sum())
rows_out = len(df)
df = df.dropna(subset=['Unit_Price'])
rows_out = len(df)
cleaning_log.append({'step': 'recover_drop_unit_price', 'rows_in': rows_in, 'rows_out': rows_out, 'count_affected': unit_price_recovered + (rows_in - rows_out)})
rows_in = rows_out

corrupt = int((df['Discount'] > 0.5).sum())
df.loc[df['Discount'] > 0.5, 'Discount'] = 0.0
df['Sales'] = (df['Unit_Price'] * df['Quantity'] * (1.0 - df['Discount'])).round(2)
df['Profit'] = ((df['Unit_Price'] - df['Cost']) * df['Quantity'] * (1.0 - df['Discount'])).round(2)
cleaning_log.append({'step': 'fix_corrupt_discounts', 'rows_in': rows_in, 'rows_out': rows_in, 'count_affected': corrupt})
print('UNIT_PRICE_UNRECOVERABLE_DROPPED', int(df.isna().sum().sum()))
print('CORRUPT_DISCOUNT_GT05', corrupt)

assert (df['Quantity'] > 0).all()
assert ((df['Discount'] >= 0) & (df['Discount'] <= 0.2)).all()
for c in ['Customer_ID','Order_ID','Product_ID','Unit_Price','Cost','Quantity','Discount','Sales','Profit']:
    assert df[c].notna().all()
print('ASSERT_OK')

df['Order_Date'] = pd.to_datetime(df['Order_Date'])
snapshot = df['Order_Date'].max() + timedelta(days=1)

print('RAW_ROWS_BEFORE_DEDUP', rows_before_dedup)
print('ROWS_AFTER_DEDUP', rows_after_dedup if 'rows_after_dedup' in locals() else rows_out)
print('FINAL_ROWS', len(df))
print('PCT_RETAINED', len(df) / rows_before_dedup * 100)

cleaning_log_df = pd.DataFrame(cleaning_log)
cleaning_log_df.to_csv(os.path.join(OUTDIR, 'cleaning_log.csv'), index=False)
print(cleaning_log_df.to_string(index=False))

# STEP B: FEATURES
print('\n--- FEATURES ---')
cust = df.groupby('Customer_ID').agg(
    Total_Spend=('Sales', 'sum'),
    Total_Profit=('Profit', 'sum'),
    Num_Orders=('Order_ID', lambda x: x.nunique()),
    Avg_Items_Per_Order=('Quantity', 'mean'),
    Avg_Discount=('Discount', 'mean'),
    Customer_Age=('Customer_Age', 'first'),
).reset_index()
cust['Avg_Order_Value'] = cust['Total_Spend'] / cust['Num_Orders']
last_order = df.groupby('Customer_ID')['Order_Date'].max().reset_index()
last_order['Recency_Days'] = (snapshot - last_order['Order_Date']).dt.days
cust = cust.merge(last_order[['Customer_ID', 'Recency_Days']], on='Customer_ID')
cust.to_csv(os.path.join(OUTDIR, 'customer_features.csv'), index=False)

vif_cols = ['Total_Spend', 'Total_Profit', 'Num_Orders', 'Avg_Order_Value', 'Recency_Days', 'Avg_Items_Per_Order', 'Avg_Discount']
Xv = cust[vif_cols].copy()
corr = Xv.corr()
print('\nCORRELATION_MATRIX')
print(corr.to_string())
corr.to_csv(os.path.join(OUTDIR, 'correlation_matrix.csv'))

vif_rows = []
for i in range(Xv.shape[1]):
    X = Xv.iloc[:, [j for j in range(Xv.shape[1]) if j != i]]
    y = Xv.iloc[:, i]
    lr = LinearRegression().fit(X, y)
    r2 = lr.score(X, y)
    vif = 1.0 / (1.0 - r2) if (1.0 - r2) > 1e-12 else np.inf
    vif_rows.append((vif_cols[i], vif))
vif_df = pd.DataFrame(vif_rows, columns=['feature', 'VIF'])
print('\nVIF')
print(vif_df.to_string())
vif_df.to_csv(os.path.join(OUTDIR, 'vif.csv'), index=False)

skew_before = Xv.skew()
print('\nSKEW_BEFORE')
print(skew_before.to_string())
skew_before.to_csv(os.path.join(OUTDIR, 'skew_before.csv'))

Xv_log = Xv.copy()
for c in Xv_log.columns:
    if abs(skew_before[c]) > 1:
        Xv_log[c] = np.log1p(Xv_log[c])
skew_after = Xv_log.skew()
print('\nSKEW_AFTER_LOG1P')
print(skew_after.to_string())
skew_after.to_csv(os.path.join(OUTDIR, 'skew_after.csv'))

# STEP C: CLUSTERING FEATURES
print('\n--- CLUSTERING FEATURES ---')
clust_cols = ['Num_Orders', 'Avg_Order_Value', 'Recency_Days', 'Avg_Items_Per_Order']
print('CLUSTER_FEATURES', clust_cols)
Xc = cust[clust_cols].copy()
for c in clust_cols:
    if abs(skew_before[c]) > 1:
        Xc[c] = np.log1p(Xc[c])
scaler = StandardScaler()
Xs = scaler.fit_transform(Xc)

# STEP D: K SELECTION
print('\n--- K SELECTION ---')
kres = []
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=50, random_state=42)
    lab = km.fit_predict(Xs)
    kres.append({
        'k': k,
        'inertia': km.inertia_,
        'silhouette': silhouette_score(Xs, lab),
        'davies_bouldin': davies_bouldin_score(Xs, lab),
        'calinski_harabasz': calinski_harabasz_score(Xs, lab),
    })
kdf = pd.DataFrame(kres)
print(kdf.to_string(index=False))
kdf.to_csv(os.path.join(OUTDIR, 'k_selection.csv'), index=False)
best_sil_k_res = int(kdf.loc[kdf['silhouette'].idxmax(), 'k'])
print('BEST_SIL_K', best_sil_k_res)

# STEP E: EVALUATION
cust_eval = cust.merge(labels, on='Customer_ID', how='left')


def eval_k(k):
    print('\n=== K', k, '===')
    km = KMeans(n_clusters=k, n_init=50, random_state=42)
    ref = km.fit_predict(Xs)

    aris_seed = []
    for rs in range(20):
        km2 = KMeans(n_clusters=k, n_init=50, random_state=rs)
        pred = km2.fit_predict(Xs)
        aris_seed.append(adjusted_rand_score(ref, pred))
    print('SEED_STABILITY_MEAN', np.mean(aris_seed), 'STD', np.std(aris_seed))

    aris_boot = []
    for b in range(20):
        idxb = np.random.RandomState(b).choice(len(Xs), len(Xs), replace=True)
        Xb = Xs[idxb]
        km_b = KMeans(n_clusters=k, n_init=50, random_state=42)
        km_b.fit(Xb)
        pred_full = km_b.predict(Xs)
        aris_boot.append(adjusted_rand_score(ref, pred_full))
    print('BOOTSTRAP_ARI_LIST', aris_boot)
    print('BOOTSTRAP_ARI_MEAN', np.mean(aris_boot), 'STD', np.std(aris_boot))

    ce = cust_eval.copy()
    ce['cluster'] = ref
    ct = pd.crosstab(ce['Latent_Type_Name'], ce['cluster'])
    print('\nCONFUSION_TABLE')
    print(ct.to_string())
    ct.to_csv(os.path.join(OUTDIR, f'confusion_k{k}.csv'))
    print('ARI_GT', adjusted_rand_score(ce['Latent_Type_Name'], ref))
    print('NMI_GT', normalized_mutual_info_score(ce['Latent_Type_Name'], ref))
    if k == 5:
        print('LARGEST_CLUSTER_SHARE_BY_LATENT_TYPE')
        for lt in sorted(ce['Latent_Type_Name'].unique()):
            sub = ce[ce['Latent_Type_Name'] == lt]
            vc = sub['cluster'].value_counts()
            print(f'  {lt}: largest_cluster={vc.index[0]} share={vc.iloc[0] / len(sub):.3f}')

    gd = [ce[ce['cluster'] == c]['Avg_Discount'].values for c in range(k)]
    ga = [ce[ce['cluster'] == c]['Customer_Age'].values for c in range(k)]
    print('KRUSKAL_AVG_DISCOUNT', kruskal(*gd))
    print('KRUSKAL_AGE', kruskal(*ga))
    return ref


for k in sorted(set([4, 5, best_sil_k_res])):
    eval_k(k)

# STEP F: ALGORITHM COMPARISON at k=4 and k=5
print('\n--- ALGORITHM COMPARISON ---')
from sklearn.mixture import GaussianMixture
from sklearn.cluster import AgglomerativeClustering


def cluster_labels(method, k, X):
    if method == 'KMeans':
        return KMeans(n_clusters=k, n_init=50, random_state=42).fit_predict(X)
    if method == 'GMM':
        return GaussianMixture(n_components=k, n_init=5, random_state=42).fit_predict(X)
    if method == 'Agglomerative':
        return AgglomerativeClustering(n_clusters=k, linkage='ward').fit_predict(X)


for k in [4, 5]:
    print(f'=== K={k} algorithm comparison ===')
    for method in ['KMeans', 'GMM', 'Agglomerative']:
        pred = cluster_labels(method, k, Xs)
        sil = silhouette_score(Xs, pred)
        db = davies_bouldin_score(Xs, pred)
        ari = adjusted_rand_score(cust_eval['Latent_Type_Name'], pred)
        nmi = normalized_mutual_info_score(cust_eval['Latent_Type_Name'], pred)
        print(f'{method}: silhouette={sil:.4f} davies_bouldin={db:.4f} ARI_GT={ari:.4f} NMI_GT={nmi:.4f}')

# STEP G: SEGMENT PROFILE for k=5
print('\n--- SEGMENT PROFILE k=5 ===')
k = 5
seg_labels = KMeans(n_clusters=k, n_init=50, random_state=42).fit_predict(Xs)
seg = cust_eval.copy()
seg['segment'] = ['S%d' % c for c in seg_labels]
total_rev = seg['Total_Spend'].sum()
total_profit = seg['Total_Profit'].sum()
n_cust = len(seg)
rows = []
for s in sorted(seg['segment'].unique()):
    g = seg[seg['segment'] == s]
    dom = g['Latent_Type_Name'].value_counts()
    dom_name = dom.index[0]
    dom_share = dom.iloc[0] / len(g)
    print(f'{s}: size={len(g)} pct_cust={len(g)/n_cust*100:.1f} pct_rev={g["Total_Spend"].sum()/total_rev*100:.1f} pct_profit={g["Total_Profit"].sum()/total_profit*100:.1f} '
          f'mean_Num_Orders={g["Num_Orders"].mean():.2f} mean_AOV={g["Avg_Order_Value"].mean():.2f} mean_Recency={g["Recency_Days"].mean():.1f} '
          f'mean_Items={g["Avg_Items_Per_Order"].mean():.2f} mean_Discount={g["Avg_Discount"].mean():.3f} dominant={dom_name} ({dom_share*100:.1f}%)')
    rows.append({
        'segment': s,
        'size': len(g),
        'pct_cust': len(g) / n_cust * 100,
        'pct_rev': g['Total_Spend'].sum() / total_rev * 100,
        'pct_profit': g['Total_Profit'].sum() / total_profit * 100,
        'mean_Num_Orders': g['Num_Orders'].mean(),
        'mean_AOV': g['Avg_Order_Value'].mean(),
        'mean_Recency': g['Recency_Days'].mean(),
        'mean_Items': g['Avg_Items_Per_Order'].mean(),
        'mean_Discount': g['Avg_Discount'].mean(),
        'dominant': dom_name,
        'dominant_share': dom_share,
    })
seg_profile = pd.DataFrame(rows)
seg_profile.to_csv(os.path.join(OUTDIR, 'segment_profile_k5.csv'), index=False)
seg_labels_df = seg[['Customer_ID', 'Latent_Type_Name', 'segment']].copy()
seg_labels_df.columns = ['Customer_ID', 'Latent_Type_Name', 'cluster']
seg_labels_df.to_csv(os.path.join(OUTDIR, 'customer_labels_k5.csv'), index=False)

# STEP H: SUPERVISED CEILING
print('\n--- SUPERVISED CEILING ---')
rf_df = cust_eval.dropna(subset=['Latent_Type_Name']).copy()
y = rf_df['Latent_Type'].values
Xrf = rf_df[clust_cols].copy()
for c in clust_cols:
    if abs(skew_before[c]) > 1:
        Xrf[c] = np.log1p(Xrf[c])
Xrf_s = StandardScaler().fit_transform(Xrf)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
rf = RandomForestClassifier(n_estimators=300, random_state=42)
y_pred = cross_val_predict(rf, Xrf_s, y, cv=cv)
acc = accuracy_score(y, y_pred)
f1 = f1_score(y, y_pred, average='macro')
print('SUPERVISED_ACCURACY', acc)
print('SUPERVISED_MACRO_F1', f1)
cm = confusion_matrix(y, y_pred, labels=sorted(rf_df['Latent_Type'].unique()))
cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True)
print('SUPERVISED_CONFUSION_MATRIX_ROW_NORMALIZED')
print(np.array2string(cm_norm, precision=3, suppress_small=True))

