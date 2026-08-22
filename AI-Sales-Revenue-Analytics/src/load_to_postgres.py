"""
Load cleaned CSV into PostgreSQL using `sql/database_schema.sql` schema.
Requires a running PostgreSQL instance and environment variables in a .env file:

PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

Usage:
    pip install -r requirements.txt
    set environment variables or create .env in project root
    python src/load_to_postgres.py

The script will:
- execute the SQL schema to create tables if they do not exist
- read `data/processed/cleaned_sales_data.csv`
- normalize into customers, products, orders, order_details
- bulk insert into the database

Note: Run only after confirming DB credentials. The script is safe to re-run (it deduplicates by primary keys).
"""
import os
from urllib.parse import quote_plus
import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd
from dotenv import load_dotenv

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(PROJ_ROOT, '.env'))
PGHOST = os.getenv('PGHOST', 'localhost')
PGPORT = os.getenv('PGPORT', '5432')
PGUSER = os.getenv('PGUSER', 'postgres')
PGPASSWORD = os.getenv('PGPASSWORD', '')
PGDATABASE = os.getenv('PGDATABASE', 'retailx')

CLEAN_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'cleaned_sales_data.csv')
SCHEMA_SQL = os.path.join(PROJ_ROOT, 'sql', 'database_schema.sql')

def ensure_database_exists():
    """Create the target database once, using PostgreSQL's default database."""
    connection = psycopg2.connect(
        host=PGHOST,
        port=PGPORT,
        user=PGUSER,
        password=PGPASSWORD,
        dbname='postgres'
    )
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (PGDATABASE,))
            if cursor.fetchone() is None:
                cursor.execute(f'CREATE DATABASE "{PGDATABASE.replace(chr(34), chr(34) * 2)}"')
                print(f'Created PostgreSQL database: {PGDATABASE}')
    finally:
        connection.close()

if __name__ == '__main__':
    if not os.path.exists(CLEAN_PATH):
        raise SystemExit(f'Cleaned CSV not found at {CLEAN_PATH}. Run data cleaning first.')

    ensure_database_exists()
    # Encode credentials so special characters in the password do not corrupt the URL.
    engine_url = f'postgresql+psycopg2://{quote_plus(PGUSER)}:{quote_plus(PGPASSWORD)}@{PGHOST}:{PGPORT}/{PGDATABASE}'
    engine = create_engine(engine_url)

    # Execute schema
    with open(SCHEMA_SQL, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    with engine.begin() as conn:
        conn.exec_driver_sql(schema_sql)

    # Load cleaned data
    df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])

    # Prepare customers
    customers = df[['Customer_ID','Customer_Name','Customer_Age','Customer_Gender','Customer_Segment','City','State','Region']].drop_duplicates(subset=['Customer_ID']).rename(columns={'Customer_ID':'customer_id','Customer_Age':'age','Customer_Gender':'gender','Customer_Segment':'segment','Customer_Name':'customer_name','City':'city','State':'state','Region':'region'})

    # Prepare products
    products = df[['Product_ID','Product_Name','Category','Sub_Category','Unit_Price','Cost']].drop_duplicates(subset=['Product_ID']).rename(columns={'Product_ID':'product_id','Product_Name':'product_name','Category':'category','Sub_Category':'sub_category','Unit_Price':'unit_price','Cost':'cost'})

    # Prepare orders
    orders = df[['Order_ID','Customer_ID','Order_Date','Ship_Date','Sales_Channel','Payment_Mode','Order_Status','Return_Flag']].drop_duplicates(subset=['Order_ID']).rename(columns={'Order_ID':'order_id','Customer_ID':'customer_id','Order_Date':'order_date','Ship_Date':'ship_date','Sales_Channel':'sales_channel','Payment_Mode':'payment_mode','Order_Status':'order_status','Return_Flag':'return_flag'})

    # Prepare order_details
    order_details = df[['Order_ID','Product_ID','Quantity','Discount','Sales','Profit']].rename(columns={'Order_ID':'order_id','Product_ID':'product_id','Quantity':'quantity','Discount':'discount','Sales':'sales','Profit':'profit'})

    # Insert data (upsert-like safe behavior: use temporary tables then insert where not exists)
    with engine.begin() as conn:
        # This project loader owns these tables and replaces their contents on each run.
        conn.exec_driver_sql('TRUNCATE TABLE order_details, orders, products, customers RESTART IDENTITY CASCADE')
        chunk_size = 500
        # customers
        customers.to_sql('customers', conn, if_exists='append', index=False, method='multi', chunksize=chunk_size)
        products.to_sql('products', conn, if_exists='append', index=False, method='multi', chunksize=chunk_size)
        orders.to_sql('orders', conn, if_exists='append', index=False, method='multi', chunksize=chunk_size)
        order_details.to_sql('order_details', conn, if_exists='append', index=False, method='multi', chunksize=chunk_size)

    print('Data loaded into PostgreSQL tables: customers, products, orders, order_details')
