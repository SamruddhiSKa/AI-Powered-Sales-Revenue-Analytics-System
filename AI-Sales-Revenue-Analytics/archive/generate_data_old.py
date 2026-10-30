"""
Synthetic Retail Sales Data Generator
Generates a realistic retail transaction dataset and writes to data/raw/sales_data.csv
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

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
    cust = pd.DataFrame({
        'Customer_ID': customer_ids,
        'Customer_Name': customer_names,
        'Customer_Segment': np.random.choice(segments, NUM_CUSTOMERS, p=[0.7,0.2,0.1]),
        'Customer_Age': np.random.randint(18,80, NUM_CUSTOMERS),
        'Customer_Gender': np.random.choice(['Male','Female','Other'], NUM_CUSTOMERS, p=[0.48,0.48,0.04])
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

def generate_dataset():
    customers = gen_customers()
    products = gen_products()

    orders = []
    order_details = []

    order_dates = random_dates(NUM_ORDERS, start_date, end_date)
    order_dates.sort()

    for i in range(NUM_ORDERS):
        order_id = f'O{100000+i}'
        cust = customers.sample(1).iloc[0]
        order_date = order_dates[i]
        ship_delay = np.random.poisson(3)
        ship_date = order_date + timedelta(days=int(ship_delay))
        sales_channel = np.random.choice(sales_channels, p=[0.6,0.3,0.1])
        payment_mode = np.random.choice(payment_modes, p=[0.5,0.2,0.2,0.1])
        order_status = np.random.choice(order_statuses, p=[0.85,0.1,0.03,0.02])
        return_flag = 1 if order_status=='Returned' else 0

        # number of items in order
        n_items = np.random.choice([1,2,3,4], p=[0.6,0.25,0.1,0.05])

        orders.append((order_id, cust['Customer_ID'], order_date.strftime('%Y-%m-%d'), ship_date.strftime('%Y-%m-%d'), sales_channel, payment_mode, order_status, return_flag))

        chosen_products = products.sample(n_items)
        for _, prod in chosen_products.iterrows():
            qty = int(max(1, np.random.poisson(2)))
            discount = round(np.random.choice([0,0,0.05,0.1,0.15], p=[0.6,0.2,0.1,0.07,0.03]),2)
            sales = round(prod.Unit_Price * qty * (1-discount),2)
            profit = round((prod.Unit_Price - prod.Cost) * qty * (1-discount),2)
            order_details.append((order_id, prod.Product_ID, qty, discount, sales, profit, prod.Unit_Price, prod.Cost, prod.Category, prod.Sub_Category))

    orders_df = pd.DataFrame(orders, columns=['Order_ID','Customer_ID','Order_Date','Ship_Date','Sales_Channel','Payment_Mode','Order_Status','Return_Flag'])
    details_df = pd.DataFrame(order_details, columns=['Order_ID','Product_ID','Quantity','Discount','Sales','Profit','Unit_Price','Cost','Category','Sub_Category'])

    # Merge with customer and product info for a denormalized CSV
    merged = details_df.merge(orders_df, on='Order_ID', how='left')
    merged = merged.merge(products, on='Product_ID', how='left')
    merged = merged.merge(customers, on='Customer_ID', how='left')

    # Add geographic info
    cities = ['New York','Los Angeles','Chicago','Houston','Phoenix','Philadelphia']
    states = ['NY','CA','IL','TX','AZ','PA']
    regions = ['East','West','Midwest','South']
    merged['City'] = np.random.choice(cities, len(merged))
    merged['State'] = np.random.choice(states, len(merged))
    merged['Region'] = np.random.choice(regions, len(merged))
    merged['Postal_Code'] = np.random.randint(10000,99999,len(merged)).astype(str)

    # Introduce missing values, duplicates, and outliers
    # Missing values
    for col in ['Customer_Age','Customer_Gender','Unit_Price']:
        merged.loc[merged.sample(frac=0.01, random_state=RANDOM_SEED).index, col] = np.nan

    # Duplicates: duplicate 0.5% rows
    dup = merged.sample(frac=0.005, random_state=RANDOM_SEED)
    merged = pd.concat([merged,dup], ignore_index=True)

    # Outliers: some extreme discounts and sales
    outlier_idx = merged.sample(frac=0.002, random_state=RANDOM_SEED).index
    merged.loc[outlier_idx, 'Discount'] = 0.9
    merged.loc[outlier_idx, 'Sales'] = merged.loc[outlier_idx, 'Sales'] * 5
    merged.loc[outlier_idx, 'Profit'] = merged.loc[outlier_idx, 'Profit'] * -1  # negative profit extreme

    # Shuffle
    merged = merged.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Create a clean, consistent set of columns to avoid duplicate suffixes from merges
    def pick(col_base):
        for candidate in [col_base, col_base + '_y', col_base + '_x']:
            if candidate in merged.columns:
                if merged[candidate].notna().sum() > 0:
                    return merged[candidate]
        # fallback: any column that contains the base name
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

    # Ensure output directory exists and write using project-relative absolute path
    import os
    proj_root = os.path.dirname(os.path.dirname(__file__))
    out_dir = os.path.join(proj_root, 'data', 'raw')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'sales_data.csv')
    final.to_csv(out_path, index=False)
    print(f"Saved synthetic dataset to {out_path} with {len(final)} rows")

if __name__ == '__main__':
    generate_dataset()
