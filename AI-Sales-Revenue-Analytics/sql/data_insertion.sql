-- Example PostgreSQL COPY-based data load (adjust paths)
-- Run after creating the database and placing cleaned CSV at the specified path.

-- Create tables using schema
\i database_schema.sql

-- Load using staging table and then insert into normalized tables
-- Replace the path with your local cleaned CSV path
-- COPY staging_raw FROM 'e:/Gauri/projects/AI-Powered Sales & Revenue Analytics System/AI-Sales-Revenue-Analytics/data/processed/cleaned_sales_data.csv' DELIMITER ',' CSV HEADER;

-- Then use INSERT INTO ... SELECT DISTINCT to populate customers, products, orders, order_details

-- Example (pseudo):
-- INSERT INTO customers (customer_id, customer_name, age, gender, segment, city, state, region)
-- SELECT DISTINCT Customer_ID, Customer_Name, Customer_Age, Customer_Gender, Customer_Segment, City, State, Region FROM staging_raw;

-- For bulk loads using psql, ensure the postgres user has read access to the file path, or use pgadmin/import wizard.
