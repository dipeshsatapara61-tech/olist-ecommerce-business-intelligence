import json
from pathlib import Path

notebooks_dir = Path(r"C:\Users\dipesh\OneDrive\Desktop\Project\BUSINESS ANALYST\Ecommerce-Business-Intelligence\notebooks")
notebooks_dir.mkdir(parents=True, exist_ok=True)

def create_nb(cells):
    return {
        "cells": cells,
        "metadata": {
            "language_info": {
                "name": "python",
                "version": "3.11"
            },
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

def md_cell(text):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    }

def code_cell(code):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    }

# ==========================================
# 1. 01_Exploratory_Data_Analysis.ipynb
# ==========================================
eda_cells = [
    md_cell("""# Olist E-Commerce - 01. Exploratory Data Analysis (EDA)
## Brazilian E-Commerce Public Dataset by Olist

### Objective
This notebook performs an end-to-end exploratory data audit across all 9 relational entities of the Olist e-commerce database. We examine table dimensions, missing data patterns, data types, duplicate integrity, and basic statistical distributions."""),

    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

# Project paths
PROJECT_ROOT = Path('..').resolve()
DATA_RAW = PROJECT_ROOT / 'data' / 'raw'
DATA_CLEAN = PROJECT_ROOT / 'data' / 'processed' / 'cleaned'

print("Project root:", PROJECT_ROOT)
print("Clean data directory exists:", DATA_CLEAN.exists())"""),

    md_cell("""### 1. Load All Datasets & Inspect Dimensions"""),

    code_cell("""datasets = {
    'customers': pd.read_csv(DATA_CLEAN / 'olist_customers_dataset.csv'),
    'geolocation': pd.read_csv(DATA_CLEAN / 'olist_geolocation_dataset.csv'),
    'order_items': pd.read_csv(DATA_CLEAN / 'olist_order_items_dataset.csv'),
    'order_payments': pd.read_csv(DATA_CLEAN / 'olist_order_payments_dataset.csv'),
    'order_reviews': pd.read_csv(DATA_CLEAN / 'olist_order_reviews_dataset.csv'),
    'orders': pd.read_csv(DATA_CLEAN / 'olist_orders_dataset.csv'),
    'products': pd.read_csv(DATA_CLEAN / 'olist_products_dataset.csv'),
    'sellers': pd.read_csv(DATA_CLEAN / 'olist_sellers_dataset.csv'),
    'translation': pd.read_csv(DATA_CLEAN / 'product_category_name_translation.csv')
}

summary = []
for name, df in datasets.items():
    summary.append({
        'Dataset': name,
        'Rows': len(df),
        'Columns': len(df.columns),
        'Nulls': df.isnull().sum().sum(),
        'Memory_MB': round(df.memory_usage(deep=True).sum() / (1024**2), 2)
    })

df_summary = pd.DataFrame(summary).sort_values('Rows', ascending=False)
display(df_summary)"""),

    md_cell("""### 2. Inspect Missing Values Across Datasets"""),

    code_cell("""null_breakdown = []
for name, df in datasets.items():
    null_cols = df.isnull().sum()
    null_cols = null_cols[null_cols > 0]
    for col, count in null_cols.items():
        null_breakdown.append({
            'Dataset': name,
            'Column': col,
            'Missing_Count': count,
            'Missing_%': round((count / len(df)) * 100, 2)
        })

df_nulls = pd.DataFrame(null_breakdown)
print("Summary of columns containing missing values:")
display(df_nulls)"""),

    md_cell("""### 3. Order Status Distribution
Delivered orders comprise the vast majority (>97%) of transactional volume."""),

    code_cell("""df_orders = datasets['orders']
status_counts = df_orders['order_status'].value_counts()
status_pct = df_orders['order_status'].value_counts(normalize=True) * 100

order_status_summary = pd.DataFrame({'Orders': status_counts, 'Percentage': status_pct.round(2)})
display(order_status_summary)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x=status_counts.values, y=status_counts.index, palette='Blues_r', ax=ax)
ax.set_title('Distribution of Order Statuses', fontsize=14, fontweight='bold')
ax.set_xlabel('Total Orders')
for i, v in enumerate(status_counts.values):
    pct_val = status_pct.iloc[i]
    ax.text(v + 1000, i, f"{v:,} ({pct_val:.2f}%)", va='center')
plt.tight_layout()
plt.show()"""),

    md_cell("""### 4. Payment Method Breakdown
Credit card is overwhelmingly the dominant payment vehicle, followed by bank cash vouchers (Boleto)."""),

    code_cell("""df_pay = datasets['order_payments']
pay_summary = df_pay.groupby('payment_type').agg(
    Transactions=('order_id', 'count'),
    Total_Value=('payment_value', 'sum'),
    Avg_Installments=('payment_installments', 'mean')
).reset_index()

pay_summary['Value_%'] = (pay_summary['Total_Value'] / pay_summary['Total_Value'].sum() * 100).round(2)
pay_summary = pay_summary.sort_values('Total_Value', ascending=False)
display(pay_summary)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = ['#0084FF', '#FF8A00', '#00C49F', '#7952B3', '#AAAAAA']
ax1.pie(pay_summary['Total_Value'], labels=pay_summary['payment_type'], autopct='%1.1f%%',
        startangle=140, colors=colors, textprops={'fontsize': 10})
ax1.set_title('Revenue Share by Payment Type', fontweight='bold')

sns.barplot(data=pay_summary, x='payment_type', y='Avg_Installments', palette='Blues_d', ax=ax2)
ax2.set_title('Average Installments by Payment Type', fontweight='bold')
ax2.set_ylabel('Mean Installments')
plt.tight_layout()
plt.show()"""),

    md_cell("""### 5. Review Score Distribution
Over 57% of reviews award 5 stars, leading to a strong 4.09 platform average."""),

    code_cell("""df_rev = datasets['order_reviews']
score_counts = df_rev['review_score'].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(score_counts.index, score_counts.values, color='#0084FF', edgecolor='#071426', width=0.6)
ax.set_title(f'Customer Review Score Distribution (Mean: {df_rev["review_score"].mean():.2f}/5.00)', fontweight='bold')
ax.set_xlabel('Review Score (Stars)')
ax.set_ylabel('Count')
for bar in bars:
    yval = bar.get_height()
    pct = (yval / len(df_rev) * 100)
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1000, f'{yval:,}\\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.show()""")
]

with open(notebooks_dir / "01_Exploratory_Data_Analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(create_nb(eda_cells), f, indent=2)
print("Created 01_Exploratory_Data_Analysis.ipynb")

# ==========================================
# 2. 02_Sales_Analysis.ipynb
# ==========================================
sales_cells = [
    md_cell("""# Olist E-Commerce - 02. Sales & Product Analysis
## In-Depth Commercial Analysis, Seasonality & Product Hierarchy

### Objective
This notebook investigates revenue trajectories, sales seasonality, product category margins, freight economics, and Average Order Value (AOV) across the Brazilian marketplace."""),

    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)

PROJECT_ROOT = Path('..').resolve()
DATA_CLEAN = PROJECT_ROOT / 'data' / 'processed' / 'cleaned'

orders = pd.read_csv(DATA_CLEAN / 'olist_orders_dataset.csv', parse_dates=['order_purchase_timestamp'])
order_items = pd.read_csv(DATA_CLEAN / 'olist_order_items_dataset.csv')
products = pd.read_csv(DATA_CLEAN / 'olist_products_dataset.csv')
translation = pd.read_csv(DATA_CLEAN / 'product_category_name_translation.csv')

print("Orders:", len(orders), "| Order Items:", len(order_items), "| Products:", len(products))"""),

    md_cell("""### 1. Build Merged Commercial Fact Table"""),

    code_cell("""# Merge products with English category translation
products_en = products.merge(translation, on='product_category_name', how='left')
products_en['category'] = products_en['product_category_name_english'].fillna('other')

# Merge items with order dates and product categories
df_sales = order_items.merge(orders[['order_id', 'order_status', 'order_purchase_timestamp']], on='order_id', how='inner')
df_sales = df_sales.merge(products_en[['product_id', 'category']], on='product_id', how='left')

df_sales['total_revenue'] = df_sales['price'] + df_sales['freight_value']
df_sales['year_month'] = df_sales['order_purchase_timestamp'].dt.to_period('M')

gross_rev = df_sales['total_revenue'].sum()
prod_sales = df_sales['price'].sum()
freight_val = df_sales['freight_value'].sum()

print("Total Commercial Fact Records:", len(df_sales))
print(f"Gross Revenue: R$ {gross_rev:,.2f}")
print(f"Product Sales: R$ {prod_sales:,.2f} ({(prod_sales/gross_rev)*100:.1f}%)")
print(f"Freight Fees: R$ {freight_val:,.2f} ({(freight_val/gross_rev)*100:.1f}%)")"""),

    md_cell("""### 2. Monthly Revenue & Order Volume Trends
Notice the sharp expansion from 2016 through 2018 with key peaks in November 2017 (Black Friday) and May 2018 (Mother's Day)."""),

    code_cell("""monthly_sales = df_sales.groupby('year_month').agg(
    Gross_Revenue=('total_revenue', 'sum'),
    Product_Sales=('price', 'sum'),
    Freight=('freight_value', 'sum'),
    Orders=('order_id', 'nunique'),
    Items_Sold=('order_item_id', 'count')
).reset_index()

monthly_sales['year_month_str'] = monthly_sales['year_month'].astype(str)
monthly_sales['AOV'] = monthly_sales['Gross_Revenue'] / monthly_sales['Orders']

fig, ax1 = plt.subplots(figsize=(14, 6))

ax1.plot(monthly_sales['year_month_str'], monthly_sales['Gross_Revenue'] / 1e6, marker='o', color='#0084FF', linewidth=2.5, label='Gross Revenue (R$ M)')
ax1.plot(monthly_sales['year_month_str'], monthly_sales['Product_Sales'] / 1e6, marker='s', color='#00C49F', linewidth=2, linestyle='--', label='Product Sales (R$ M)')
ax1.plot(monthly_sales['year_month_str'], monthly_sales['Freight'] / 1e6, marker='^', color='#FF8A00', linewidth=2, linestyle=':', label='Freight (R$ M)')
ax1.set_ylabel('Revenue (R$ Millions)', fontsize=12, fontweight='bold')
ax1.set_title('Monthly Revenue Progression (2016 - 2018)', fontsize=14, fontweight='bold')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')

ax2 = ax1.twinx()
ax2.bar(monthly_sales['year_month_str'], monthly_sales['Orders'], alpha=0.15, color='#7952B3', label='Order Volume')
ax2.set_ylabel('Total Orders', fontsize=12, fontweight='bold')
ax2.grid(False)

plt.tight_layout()
plt.show()"""),

    md_cell("""### 3. Product Category Pareto Analysis (Top 10 Categories)
Evaluating the top merchandise drivers on the platform."""),

    code_cell("""cat_perf = df_sales.groupby('category').agg(
    Revenue=('total_revenue', 'sum'),
    Product_Sales=('price', 'sum'),
    Freight=('freight_value', 'sum'),
    Orders=('order_id', 'nunique'),
    Units_Sold=('order_item_id', 'count')
).reset_index()

cat_perf = cat_perf.sort_values('Revenue', ascending=False).reset_index(drop=True)
cat_perf['Cumulative_Revenue_%'] = (cat_perf['Revenue'].cumsum() / cat_perf['Revenue'].sum() * 100).round(2)
cat_perf['Avg_Price'] = (cat_perf['Product_Sales'] / cat_perf['Units_Sold']).round(2)

print("Top 10 Categories by Revenue:")
display(cat_perf.head(10))

# Plot top 10 categories
fig, ax = plt.subplots(figsize=(12, 6))
top10 = cat_perf.head(10)
bars = ax.barh(top10['category'][::-1], top10['Revenue'][::-1] / 1e6, color='#0084FF')
ax.set_title('Top 10 Product Categories by Gross Revenue (R$ Millions)', fontsize=14, fontweight='bold')
ax.set_xlabel('Gross Revenue (R$ Millions)')
for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.02, bar.get_y() + bar.get_height()/2, f'R$ {w:.2f}M', va='center', fontsize=10)
plt.tight_layout()
plt.show()"""),

    md_cell("""### 4. Freight Ratio Analysis Across Categories
Investigating how freight burdens vary across product categories."""),

    code_cell("""top15 = cat_perf.head(15).copy()
top15['Freight_Ratio_%'] = (top15['Freight'] / top15['Revenue'] * 100).round(2)
top15 = top15.sort_values('Freight_Ratio_%', ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=top15, x='Freight_Ratio_%', y='category', palette='Oranges_r', ax=ax)
ax.set_title('Freight Share of Total Order Value (Top 15 Categories)', fontsize=14, fontweight='bold')
ax.set_xlabel('Freight % of Total Revenue')
for i, v in enumerate(top15['Freight_Ratio_%']):
    ax.text(v + 0.3, i, f'{v:.1f}%', va='center', fontsize=10)
plt.tight_layout()
plt.show()""")
]

with open(notebooks_dir / "02_Sales_Analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(create_nb(sales_cells), f, indent=2)
print("Created 02_Sales_Analysis.ipynb")

# ==========================================
# 3. 03_Customer_Analysis.ipynb
# ==========================================
cust_cells = [
    md_cell("""# Olist E-Commerce - 03. Customer & Logistics Analysis
## Geographic Demographics, Repeat Purchase Cohorts & Delivery SLA vs Customer Satisfaction

### Objective
This notebook analyzes buyer demographics, regional concentration across Brazilian states, repeat customer rates, and the empirical correlation between delivery transit speed and review scores."""),

    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)

PROJECT_ROOT = Path('..').resolve()
DATA_CLEAN = PROJECT_ROOT / 'data' / 'processed' / 'cleaned'

customers = pd.read_csv(DATA_CLEAN / 'olist_customers_dataset.csv')
orders = pd.read_csv(DATA_CLEAN / 'olist_orders_dataset.csv', parse_dates=[
    'order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date'
])
reviews = pd.read_csv(DATA_CLEAN / 'olist_order_reviews_dataset.csv')
sellers = pd.read_csv(DATA_CLEAN / 'olist_sellers_dataset.csv')
order_items = pd.read_csv(DATA_CLEAN / 'olist_order_items_dataset.csv')

print("Loaded all datasets successfully.")"""),

    md_cell("""### 1. Customer Geographic Concentration (State & City Level)"""),

    code_cell("""df_cust_orders = orders.merge(customers, on='customer_id', how='inner')
state_orders = df_cust_orders['customer_state'].value_counts()
state_pct = (state_orders / len(df_cust_orders) * 100).round(2)

state_summary = pd.DataFrame({'Orders': state_orders, 'Percentage': state_pct}).head(10)
print("Top 10 States by Order Volume:")
display(state_summary)

fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(x=state_summary.index, y=state_summary['Orders'], palette='Blues_r', ax=ax)
ax.set_title('Top 10 Customer States by Order Volume', fontsize=14, fontweight='bold')
ax.set_ylabel('Total Orders')
for i, v in enumerate(state_summary['Orders']):
    pct_val = state_summary['Percentage'].iloc[i]
    ax.text(i, v + 800, f'{v:,}\\n({pct_val}%)', ha='center', fontsize=9)
plt.tight_layout()
plt.show()"""),

    md_cell("""### 2. Repeat Customer Rate Analysis
Assessing customer loyalty and multi-order frequency."""),

    code_cell("""cust_freq = customers.groupby('customer_unique_id').agg(
    Order_Count=('customer_id', 'count')
).reset_index()

repeat_custs = cust_freq[cust_freq['Order_Count'] > 1]
repeat_rate = (len(repeat_custs) / len(cust_freq)) * 100

print(f"Total Unique Customers: {len(cust_freq):,}")
print(f"Repeat Customers (2+ orders): {len(repeat_custs):,} ({repeat_rate:.2f}%)")

fig, ax = plt.subplots(figsize=(6, 4))
freq_dist = cust_freq['Order_Count'].value_counts().sort_index().head(5)
ax.bar(freq_dist.index.astype(str), freq_dist.values, color=['#0084FF', '#FF8A00', '#00C49F', '#7952B3', '#AAAAAA'])
ax.set_title('Customer Order Frequency Distribution', fontweight='bold')
ax.set_xlabel('Number of Orders Placed')
ax.set_ylabel('Number of Customers')
for i, v in enumerate(freq_dist.values):
    ax.text(i, v + 1000, f'{v:,}', ha='center', fontsize=9)
plt.tight_layout()
plt.show()"""),

    md_cell("""### 3. Delivery SLA & Transit Performance
Examining transit days vs. promised estimated delivery dates for completed deliveries."""),

    code_cell("""delivered = orders[orders['order_status'] == 'delivered'].dropna(subset=['order_delivered_customer_date']).copy()

# Calculate delivery days
delivered['actual_delivery_days'] = (delivered['order_delivered_customer_date'] - delivered['order_purchase_timestamp']).dt.total_seconds() / (24 * 3600)
delivered['estimated_delivery_days'] = (delivered['order_estimated_delivery_date'] - delivered['order_purchase_timestamp']).dt.total_seconds() / (24 * 3600)
delivered['delivery_delay_days'] = (delivered['order_delivered_customer_date'] - delivered['order_estimated_delivery_date']).dt.total_seconds() / (24 * 3600)

delivered['is_on_time'] = delivered['order_delivered_customer_date'] <= delivered['order_estimated_delivery_date']

on_time_rate = delivered['is_on_time'].mean() * 100

print(f"Delivered Orders Audited: {len(delivered):,}")
print(f"Average Actual Transit Days: {delivered['actual_delivery_days'].mean():.2f} days")
print(f"Average Estimated SLA: {delivered['estimated_delivery_days'].mean():.2f} days")
print(f"On-Time Delivery Rate: {on_time_rate:.2f}%")"""),

    md_cell("""### 4. Correlation Between Delivery Speed and Customer Satisfaction (Review Scores)
Analyzing how delivery delays destroy review ratings."""),

    code_cell("""df_del_rev = delivered.merge(reviews[['order_id', 'review_score']], on='order_id', how='inner')

# Categorize delivery outcome
def categorize_delivery(row):
    delay = row['delivery_delay_days']
    if delay <= -5:
        return 'Delivered > 5 Days Early'
    elif delay <= 0:
        return 'Delivered 0-5 Days Early'
    elif delay <= 5:
        return 'Delayed 1-5 Days'
    else:
        return 'Delayed > 5 Days'

df_del_rev['delivery_category'] = df_del_rev.apply(categorize_delivery, axis=1)

sla_review_summary = df_del_rev.groupby('delivery_category').agg(
    Orders=('order_id', 'count'),
    Avg_Review_Score=('review_score', 'mean'),
    Pct_5_Star=('review_score', lambda x: (x == 5).mean() * 100),
    Pct_1_Star=('review_score', lambda x: (x == 1).mean() * 100)
).reindex([
    'Delivered > 5 Days Early',
    'Delivered 0-5 Days Early',
    'Delayed 1-5 Days',
    'Delayed > 5 Days'
]).reset_index()

display(sla_review_summary.round(2))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

sns.barplot(data=sla_review_summary, x='delivery_category', y='Avg_Review_Score', palette='RdYlGn_r', ax=ax1)
ax1.set_title('Average Review Score by Delivery Timeliness', fontweight='bold')
ax1.set_ylabel('Mean Rating (1-5 Stars)')
ax1.set_ylim(1, 5)
ax1.tick_params(axis='x', rotation=20)
for i, v in enumerate(sla_review_summary['Avg_Review_Score']):
    ax1.text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')

sns.barplot(data=sla_review_summary, x='delivery_category', y='Pct_1_Star', palette='Reds', ax=ax2)
ax2.set_title('Share of 1-Star Bad Reviews by Timeliness', fontweight='bold')
ax2.set_ylabel('% 1-Star Reviews')
ax2.tick_params(axis='x', rotation=20)
for i, v in enumerate(sla_review_summary['Pct_1_Star']):
    ax2.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontweight='bold')

plt.tight_layout()
plt.show()""")
]

with open(notebooks_dir / "03_Customer_Analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(create_nb(cust_cells), f, indent=2)
print("Created 03_Customer_Analysis.ipynb")
