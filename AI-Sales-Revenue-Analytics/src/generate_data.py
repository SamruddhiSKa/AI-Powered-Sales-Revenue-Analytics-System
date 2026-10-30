"""
Synthetic Retail Sales Data Generator
Generates a realistic retail transaction dataset and writes to data/raw/sales_data.csv
"""
import argparse
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

try:
    from . import config
except ImportError:
    import config

RANDOM_SEED = getattr(config, 'SEED', 42)
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

LATENT_TYPES = {
    0: {'name': 'Bargain Hunters',     'order_rate': 0.6, 'basket_size': 1.2, 'discount_sensitivity': 0.8, 'recency_bias': 0.3},
    1: {'name': 'Loyal Regulars',      'order_rate': 1.0, 'basket_size': 1.0, 'discount_sensitivity': 0.3, 'recency_bias': 0.7},
    2: {'name': 'Big Spenders',        'order_rate': 0.8, 'basket_size': 1.8, 'discount_sensitivity': 0.2, 'recency_bias': 0.6},
    3: {'name': 'Occasional Shoppers', 'order_rate': 0.4, 'basket_size': 0.8, 'discount_sensitivity': 0.5, 'recency_bias': 0.2},
    4: {'name': 'Impulse Buyers',      'order_rate': 0.9, 'basket_size': 1.3, 'discount_sensitivity': 0.6, 'recency_bias': 0.5},
}

NUM_CUSTOMERS = 3000
NUM_PRODUCTS = 500
NUM_ORDERS = 20000  # adjust between 10k-50k as needed

start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 12, 31)

def random_dates(n, start, end):
    start_u = start.value // 10**9 if hasattr(start, 'value') else int(start.timestamp())
    end_u = int(end.timestamp())
    return [datetime.fromtimestamp(random.randint(int(start.timestamp()), end_u)) for _ in range(n)]

# Customers
customer_ids = [f'C{1000+i}' for i in range(NUM_CUSTOMERS)]
customer_names = [f'Customer_{i}' for i in range(NUM_CUSTOMERS)]
segments = ['Consumer', 'Corporate', 'Home Office']

def gen_customers():
    customer_ids = [f'C{1000+i}' for i in range(NUM_CUSTOMERS)]
    customer_names = [f'Customer_{i}' for i in range(NUM_CUSTOMERS)]
    segments = ['Consumer', 'Corporate', 'Home Office']
    latent_types = np.random.choice(list(LATENT_TYPES.keys()), NUM_CUSTOMERS)
    cust = pd.DataFrame({
        'Customer_ID': customer_ids,
        'Customer_Name': customer_names,
        'Customer_Segment': np.random.choice(segments, NUM_CUSTOMERS, p=[0.7,0.2,0.1]),
        'Customer_Age': np.random.randint(18,80, NUM_CUSTOMERS),
        'Customer_Gender': np.random.choice(['Male','Female','Other'], NUM_CUSTOMERS, p=[0.48,0.48,0.04]),
        'Latent_Type': latent_types,
        'Latent_Type_Name': [LATENT_TYPES[t]['name'] for t in latent_types],
    })
    return cust

# Products
categories = ['Electronics','Furniture','Office Supplies','Clothing','Home & Kitchen']
sub_categories = {
    'Electronics':['Phones','Computers','Accessories'],
    'Furniture':['Chairs','Tables','Storage'],
    'Office Supplies':['Paper','Writing','Binders'],
    'Clothing':['Men','Women','Kids'],
    'Home & Kitchen':['Kitchen','Decor','Bedding']
}

def gen_products():
    pids = [f'P{1000+i}' for i in range(NUM_PRODUCTS)]
    rows = []
    for i,pid in enumerate(pids):
        cat = np.random.choice(categories, p=[0.25,0.15,0.25,0.2,0.15])
        sub = np.random.choice(sub_categories[cat])
        unit_price = round(abs(np.random.normal(50 if cat=='Office Supplies' else 200, 80)),2)
        cost = round(unit_price * np.random.uniform(0.4,0.8),2)
        rows.append((pid, f'Product_{i}', cat, sub, unit_price, cost))
    prod = pd.DataFrame(rows, columns=['Product_ID','Product_Name','Category','Sub_Category','Unit_Price','Cost'])
    return prod

# Orders and order_details
sales_channels = ['Online','Retail','Phone']
payment_modes = ['Credit Card','Debit Card','Cash','Net Banking']
order_statuses = ['Completed','Shipped','Cancelled','Returned']

def generate_dataset(return_customers=False):
    rng = np.random.default_rng(RANDOM_SEED)
    customers = gen_customers()
    products = gen_products()

    lt = customers['Latent_Type'].to_numpy()
    order_rate = np.array([LATENT_TYPES[t]['order_rate'] for t in lt])
    basket_size = np.array([LATENT_TYPES[t]['basket_size'] for t in lt])
    discount_sensitivity = np.array([LATENT_TYPES[t]['discount_sensitivity'] for t in lt])
    recency_bias = np.array([LATENT_TYPES[t]['recency_bias'] for t in lt])
    cust_ids_arr = customers['Customer_ID'].to_numpy()

    orders = []
    order_details = []

    w = order_rate * rng.lognormal(0, 0.3, NUM_CUSTOMERS)
    probs = w / w.sum()
    cust_idx = rng.choice(NUM_CUSTOMERS, size=NUM_ORDERS, p=probs)

    frac = rng.beta(0.5 + 8 * recency_bias[cust_idx], 0.5 + 8 * (1 - recency_bias[cust_idx]))
    o = np.argsort(frac)
    frac, cust_idx = frac[o], cust_idx[o]
    span = (end_date - start_date).total_seconds()
    order_dates = [start_date + timedelta(seconds=float(f * span)) for f in frac]

    for i in range(NUM_ORDERS):
        order_id = f'O{100000+i}'
        c = cust_idx[i]
        cust_id = cust_ids_arr[c]
        order_date = order_dates[i]
        ship_delay = int(rng.poisson(3))
        ship_date = order_date + timedelta(days=ship_delay)
        sales_channel = rng.choice(sales_channels, p=[0.6,0.3,0.1])
        payment_mode = rng.choice(payment_modes, p=[0.5,0.2,0.2,0.1])
        order_status = rng.choice(order_statuses, p=[0.85,0.1,0.03,0.02])
        return_flag = 1 if order_status=='Returned' else 0

        n_items = int(np.clip(1 + rng.poisson(0.7 * basket_size[c]), 1, 6))

        orders.append((order_id, cust_id, order_date.strftime('%Y-%m-%d'), ship_date.strftime('%Y-%m-%d'), sales_channel, payment_mode, order_status, return_flag))

        chosen_products = products.sample(n_items, random_state=int(rng.integers(10**9)))
        for _, prod in chosen_products.iterrows():
            qty = int(max(1, rng.poisson(2 * basket_size[c])))
            if rng.random() < discount_sensitivity[c]:
                discount = float(rng.choice([0.05, 0.10, 0.15, 0.20]))
            else:
                discount = 0.0
            discount = round(discount, 2)
            sales = round(prod.Unit_Price * qty * (1-discount),2)
            profit = round((prod.Unit_Price - prod.Cost) * qty * (1-discount),2)
            order_details.append((order_id, prod.Product_ID, qty, discount, sales, profit, prod.Unit_Price, prod.Cost, prod.Category, prod.Sub_Category))

    orders_df = pd.DataFrame(orders, columns=['Order_ID','Customer_ID','Order_Date','Ship_Date','Sales_Channel','Payment_Mode','Order_Status','Return_Flag'])
    details_df = pd.DataFrame(order_details, columns=['Order_ID','Product_ID','Quantity','Discount','Sales','Profit','Unit_Price','Cost','Category','Sub_Category'])

    merged = details_df.merge(orders_df, on='Order_ID', how='left')
    merged = merged.merge(products[['Product_ID', 'Product_Name']], on='Product_ID', how='left')
    merged = merged.merge(customers[['Customer_ID', 'Customer_Name', 'Customer_Segment', 'Customer_Age', 'Customer_Gender']], on='Customer_ID', how='left')

    cities = ['New York','Los Angeles','Chicago','Houston','Phoenix','Philadelphia']
    states = ['NY','CA','IL','TX','AZ','PA']
    regions = ['East','West','Midwest','South']
    merged['City'] = rng.choice(cities, len(merged))
    merged['State'] = rng.choice(states, len(merged))
    merged['Region'] = rng.choice(regions, len(merged))
    merged['Postal_Code'] = rng.integers(10000,99999,len(merged)).astype(str)

    for j, col in enumerate(['Customer_Age','Customer_Gender','Unit_Price']):
        idx = merged.sample(frac=0.01, random_state=RANDOM_SEED + j).index
        merged.loc[idx, col] = np.nan

    dup = merged.sample(frac=0.005, random_state=RANDOM_SEED + 10)
    merged = pd.concat([merged,dup], ignore_index=True)

    outlier_idx = merged.sample(frac=0.002, random_state=RANDOM_SEED + 20).index
    merged.loc[outlier_idx, 'Discount'] = 0.9
    merged.loc[outlier_idx, 'Sales'] = merged.loc[outlier_idx, 'Sales'] * 5
    merged.loc[outlier_idx, 'Profit'] = merged.loc[outlier_idx, 'Profit'] * -1

    merged = merged.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    def pick(col_base):
        for candidate in [col_base, col_base + '_y', col_base + '_x']:
            if candidate in merged.columns:
                if merged[candidate].notna().sum() > 0:
                    return merged[candidate]
        for c in merged.columns:
            if col_base in c:
                return merged[c]
        return pd.Series([None]*len(merged))

    final = pd.DataFrame()
    final['Order_ID'] = merged['Order_ID']
    final['Order_Date'] = merged['Order_Date']
    final['Ship_Date'] = merged['Ship_Date']
    final['Sales_Channel'] = merged['Sales_Channel']
    final['Payment_Mode'] = merged['Payment_Mode']
    final['Order_Status'] = merged['Order_Status']
    final['Return_Flag'] = merged['Return_Flag']
    final['Customer_ID'] = merged['Customer_ID']
    final['Customer_Name'] = merged['Customer_Name']
    final['Customer_Segment'] = merged['Customer_Segment']
    final['Customer_Age'] = merged['Customer_Age']
    final['Customer_Gender'] = merged['Customer_Gender']
    final['Product_ID'] = merged['Product_ID']
    final['Product_Name'] = merged['Product_Name']
    final['Category'] = pick('Category')
    final['Sub_Category'] = pick('Sub_Category')
    final['Unit_Price'] = pick('Unit_Price')
    final['Cost'] = pick('Cost')
    final['Quantity'] = merged['Quantity']
    final['Discount'] = merged['Discount']
    final['Sales'] = merged['Sales']
    final['Profit'] = merged['Profit']
    final['City'] = merged['City']
    final['State'] = merged['State']
    final['Region'] = merged['Region']
    final['Postal_Code'] = merged['Postal_Code']

    if return_customers:
        return final, customers
    return final


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out-dir', default=os.path.join('v2', 'data', 'raw'))
    args = parser.parse_args()

    df, customers = generate_dataset(return_customers=True)
    os.makedirs(args.out_dir, exist_ok=True)

    raw_name = os.path.basename(getattr(config, 'RAW_DATA_PATH', 'sales_data.csv'))
    raw_path = os.path.join(args.out_dir, raw_name)
    df.to_csv(raw_path, index=False, encoding='utf-8')

    labels_path = os.path.join(args.out_dir, 'customer_latent_types.csv')
    customers[['Customer_ID', 'Latent_Type', 'Latent_Type_Name']].to_csv(labels_path, index=False, encoding='utf-8')

    print(f'Saved synthetic data to {raw_path} with {len(df)} rows')
    print(f'Saved latent labels to {labels_path}')
