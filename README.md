# 🛒 Olist E-Commerce Business Intelligence & Analytics

**End-to-End Data Analytics Project | Python • PostgreSQL • SQL • Power BI**

An end-to-end Business Intelligence project focused on analyzing Brazilian e-commerce operations using the Olist public e-commerce dataset. This project transforms raw transactional data into meaningful business insights through Python-based data cleaning, PostgreSQL data management, SQL analysis, and interactive Power BI dashboards.

---

## 📌 1. Project Overview

E-commerce businesses generate large amounts of transactional data, but raw data alone cannot explain business performance.

This project analyzes Olist's e-commerce operations to understand sales performance, product trends, seller performance, customer behavior, delivery efficiency, and customer satisfaction.

The goal is to convert raw business data into actionable insights that can support better business decisions.

## 🎯 2. Business Objectives

- Analyze overall revenue and order performance.
- Identify the best-performing product categories.
- Evaluate seller performance and regional distribution.
- Understand customer purchasing patterns.
- Analyze delivery performance and order statuses.
- Measure customer satisfaction through review scores.
- Identify business trends and opportunities for improvement.

## 🛠️ 3. Technologies & Tools

| Technology | Purpose |
|---|---|
| Python | Data inspection, cleaning and ETL |
| Pandas | Data manipulation and preprocessing |
| PostgreSQL | Relational database management |
| SQL | Business analysis and data validation |
| Power BI | Interactive dashboard development |
| DAX | Business metrics and calculations |
| Excel / CSV | Dataset storage and inspection |
| Git & GitHub | Version control and project documentation |

## 📂 4. Dataset Information

**Dataset:** Brazilian E-Commerce Public Dataset by Olist

The project uses nine CSV files:

1. `olist_customers_dataset.csv`
2. `olist_geolocation_dataset.csv`
3. `olist_orders_dataset.csv`
4. `olist_order_items_dataset.csv`
5. `olist_order_payments_dataset.csv`
6. `olist_order_reviews_dataset.csv`
7. `olist_products_dataset.csv`
8. `olist_sellers_dataset.csv`
9. `product_category_name_translation.csv`

The dataset contains information about customers, orders, products, sellers, payments, reviews, and geographical locations.

**Dataset period:** 2016–2018.

## ⚙️ 5. Data Analytics Workflow

The project follows an end-to-end analytics workflow.

### Step 1: Data Inspection
- Inspected all nine CSV datasets.
- Examined row counts and column structures.
- Identified missing values and duplicate records.
- Investigated data quality issues.

### Step 2: Data Quality Analysis
- Generated data quality reports.
- Investigated duplicate review IDs.
- Examined missing order timestamps.
- Identified repeated geolocation records.
- Performed primary key validation.

### Step 3: Data Cleaning Using Python
- Removed duplicate geolocation records.
- Investigated missing values.
- Prepared cleaned datasets.
- Stored processed files separately from raw datasets.

### Step 4: PostgreSQL Database Integration
- Created the `olist_ecommerce` database.
- Connected Python to PostgreSQL.
- Loaded cleaned datasets into database tables.
- Prepared relational data for SQL analysis.

### Step 5: SQL Analysis
- Analyzed revenue and order performance.
- Examined product category performance.
- Evaluated seller and customer distribution.
- Investigated delivery and review performance.

### Step 6: Power BI Visualization
Developed a four-page interactive dashboard to communicate business performance and insights.

## 📊 6. Power BI Dashboard

The dashboard contains four analytical pages.

### Page 1: Executive Overview

**Objective:** Understand overall business performance at a glance.

Key KPIs:
- Total Revenue
- Total Orders
- Total Customers
- Total Products
- Total Sellers
- Average Order Value

Visualizations:
- Monthly Revenue Trend
- Order Status Breakdown
- Revenue by Payment Type
- Top 5 Categories by Revenue
- Monthly Order Volume
- Business Performance Summary

### Page 2: Sales & Product Analysis

**Objective:** Understand revenue trends and product category performance.

Key KPIs:
- Product Sales
- Total Freight
- Total Revenue
- Total Products
- Total Orders
- Average Order Value

Visualizations:
- Monthly Revenue Trajectory
- Product Sales vs Freight
- Category Share
- Top 10 Product Categories
- Category Breakdown
- Sales Financials

### Page 3: Seller & Customer Analysis

**Objective:** Evaluate seller performance and customer distribution.

Key KPIs:
- Total Sellers
- Total Customers
- Total Orders
- Total Revenue
- Average Review Score
- Average Order Value

Visualizations:
- Top Sellers by Total Revenue
- Customers by Geographic State
- Seller Regional Concentration
- Monthly Customer Growth
- Seller Details
- Geographic Breakdown

### Page 4: Delivery & Customer Satisfaction

**Objective:** Measure delivery efficiency and customer satisfaction.

Key KPIs:
- Total Orders
- Delivered Orders
- Total Customers
- Average Review Score
- Total Products
- Total Revenue

Visualizations:
- Review Score Distribution
- Orders by State
- Order Status
- Monthly Delivered Volume
- Monthly Satisfaction Trend
- Delivery Performance by State

### Dashboard Design

- Dark navy blue background
- Electric blue and cyan accents
- White KPI cards
- Consistent typography
- Interactive filters and slicers
- Four-page navigation

## 📁 7. Project Structure

```text
Ecommerce-Business-Intelligence/
│
├── dashboard/
│   ├── Dashboard.pbix
│   ├── DAX_Measures_Reference.dax
│   └── Olist_Dashboard_Theme.json
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── cleaned/
│       └── data_quality_reports/
│
├── database/
│   ├── SQL.sql
│   ├── analysis_queries.sql
│   └── relationship_validation.sql
│
├── docs/
│   ├── 01_Project_Overview.md
│   ├── 02_Data_Dictionary.md
│   ├── 03_Data_Cleaning_Methodology.md
│   ├── 04_Business_Insights.md
│   └── 05_Dashboard_Guide.md
│
├── notebooks/
│   ├── 01_Exploratory_Data_Analysis.ipynb
│   ├── 02_Sales_Analysis.ipynb
│   └── 03_Customer_Analysis.ipynb
│
├── reports/
│   ├── Olist_Ecommerce_Business_Intelligence_Project_Documentation.pdf
│   ├── Business_Analysis_Report.pdf
│   ├── Data_Quality_Report.pdf
│   ├── SQL_Code_and_Analysis_Report.pdf
│   ├── Dashboard_Executive_Overview.png
│   ├── Dashboard_Sales_Analysis.png
│   ├── Dashboard_Seller_Customer.png
│   └── Dashboard_Delivery_Ratings.png
│
├── src/
│   ├── 01_inspect_datasets.py
│   ├── 02_data_quality_report.py
│   ├── 03_investigate_data_issues.py
│   ├── 04_clean_datasets.py
│   ├── 06_test_database_connection.py
│   └── 07_load_postgresql.py
│
├── .env
├── .gitignore
└── README.md
```

## 🚀 8. How to Run the Project

### Prerequisites

Install the following:

- Python 3.10 or later
- PostgreSQL
- pgAdmin
- Power BI Desktop
- Git

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Ecommerce-Business-Intelligence
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate
```

### Step 3: Install Dependencies

Install the Python packages used by the project:

```bash
pip install pandas numpy sqlalchemy psycopg2-binary python-dotenv
```

### Step 4: Configure PostgreSQL

Create a database named:

```sql
CREATE DATABASE olist_ecommerce;
```

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist_ecommerce
DB_USER=postgres
DB_PASSWORD=YOUR_POSTGRES_PASSWORD
```

Never upload your actual `.env` file or database password to GitHub.

### Step 5: Run Data Processing Scripts

Execute the scripts in order:

```bash
python src/01_inspect_datasets.py
python src/02_data_quality_report.py
python src/03_investigate_data_issues.py
python src/04_clean_datasets.py
```

### Step 6: Test Database Connection

```bash
python src/06_test_database_connection.py
```

### Step 7: Load Data into PostgreSQL

```bash
python src/07_load_postgresql.py
```

### Step 8: Open the Power BI Dashboard

Open:

```text
dashboard/Dashboard.pbix
```

Connect to your PostgreSQL database if required, refresh the data, and explore the four dashboard pages.

## 💡 9. Business Questions Answered

This project explores the following business questions:

1. How is the business performing in terms of revenue and orders?
2. Which product categories generate the highest revenue?
3. How do sales trends change over time?
4. Which sellers generate the highest revenue?
5. Which Brazilian states contribute the most customers and orders?
6. What are the major payment methods used by customers?
7. What percentage of orders are successfully delivered?
8. How satisfied are customers with their purchases?
9. How does delivery performance vary across geographical regions?

## 📈 10. Key Skills Demonstrated

- Exploratory Data Analysis (EDA)
- Data Cleaning and Preprocessing
- Data Quality Assessment
- Python Data Analysis
- PostgreSQL Database Management
- SQL Query Writing
- Data Integration and ETL
- Power BI Dashboard Development
- DAX Measures
- Data Visualization
- Business Intelligence
- Business Problem Solving

## 🔮 11. Future Improvements

- Automate the ETL pipeline.
- Add advanced SQL business analysis.
- Improve dashboard performance.
- Develop predictive sales analytics.
- Build customer segmentation models.
- Add automated business performance reporting.

## 👨‍💻 12. Author

**Dipesh Satapara**

Aspiring Data Analyst | Business Intelligence Enthusiast

Interested in transforming raw data into meaningful business insights using Python, SQL, PostgreSQL, and Power BI.

---

⭐ If you find this project useful, consider giving the repository a star!

**Project:** Olist E-Commerce Business Intelligence & Analytics

**Tools:** Python | PostgreSQL | SQL | Power BI | DAX