"""
Exploratory Data Analysis script that generates key figures and summary CSVs.
Saves figures to outputs/figures and summaries to outputs/insights.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
CLEAN_PATH = os.path.join(PROJ_ROOT, 'data', 'processed', 'cleaned_sales_data.csv')
OUT_FIG = os.path.join(PROJ_ROOT, 'outputs', 'figures')
OUT_INSIGHTS = os.path.join(PROJ_ROOT, 'outputs', 'insights')

os.makedirs(OUT_FIG, exist_ok=True)
os.makedirs(OUT_INSIGHTS, exist_ok=True)

# Load
if __name__ == '__main__':
    df = pd.read_csv(CLEAN_PATH, parse_dates=['Order_Date','Ship_Date'])

    # KPIs
    total_revenue = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order_ID'].nunique()
    total_customers = df['Customer_ID'].nunique()
    avg_order_value = df.groupby('Order_ID')['Sales'].sum().mean()
    profit_margin = total_profit / total_revenue if total_revenue else 0

    kpis = {
        'Total_Revenue': [total_revenue],
        'Total_Profit': [total_profit],
        'Total_Orders': [total_orders],
        'Total_Customers': [total_customers],
        'Avg_Order_Value': [avg_order_value],
        'Profit_Margin': [profit_margin]
    }
    pd.DataFrame(kpis).to_csv(os.path.join(OUT_INSIGHTS, 'kpis.csv'), index=False)

    # Monthly sales
    monthly = df.set_index('Order_Date').resample('ME').agg({'Sales':'sum','Profit':'sum'}).reset_index()
    plt.figure(figsize=(10,5))
    sns.lineplot(data=monthly, x='Order_Date', y='Sales')
    plt.title('Monthly Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'monthly_sales.png'))
    plt.close()

    # Top products by sales
    prod_sales = df.groupby(['Product_ID','Product_Name']).agg(Sales=('Sales','sum'), Profit=('Profit','sum'), Quantity=('Quantity','sum')).reset_index()
    top10 = prod_sales.sort_values('Sales', ascending=False).head(10)
    top10.to_csv(os.path.join(OUT_INSIGHTS, 'top10_products.csv'), index=False)
    plt.figure(figsize=(10,6))
    sns.barplot(data=top10, x='Sales', y='Product_Name')
    plt.title('Top 10 Products by Sales')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'top10_products.png'))
    plt.close()

    # Category-wise sales and profit
    cat = df.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    cat.to_csv(os.path.join(OUT_INSIGHTS, 'category_summary.csv'), index=False)
    plt.figure(figsize=(8,5))
    sns.barplot(data=cat.sort_values('Sales',ascending=False), x='Sales', y='Category')
    plt.title('Sales by Category')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'sales_by_category.png'))
    plt.close()

    # Discount vs Profit
    plt.figure(figsize=(8,6))
    sns.scatterplot(data=df.sample(min(2000, len(df))), x='Discount', y='Profit', alpha=0.6)
    plt.title('Discount vs Profit (sample)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'discount_vs_profit.png'))
    plt.close()

    # Customer distribution
    cust = df.groupby('Customer_ID').agg(Total_Spend=('Sales','sum')).reset_index()
    plt.figure(figsize=(8,5))
    sns.histplot(cust['Total_Spend'], bins=50)
    plt.xlim(0, cust['Total_Spend'].quantile(0.95))
    plt.title('Customer Total Spend Distribution (95% cap)')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'customer_spend_distribution.png'))
    plt.close()

    # Region performance
    region = df.groupby('Region').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    region.to_csv(os.path.join(OUT_INSIGHTS, 'region_summary.csv'), index=False)
    plt.figure(figsize=(8,4))
    sns.barplot(data=region.sort_values('Sales',ascending=False), x='Sales', y='Region')
    plt.title('Sales by Region')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_FIG, 'sales_by_region.png'))
    plt.close()

    print('EDA figures and summaries saved to outputs/figures and outputs/insights')
