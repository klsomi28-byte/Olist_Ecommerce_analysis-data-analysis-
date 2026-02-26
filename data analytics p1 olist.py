import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import os

# -----------------------
# 1️⃣ SQL CONNECTION (MySQL)
# -----------------------
engine = create_engine(
    "mysql+pymysql://root@localhost/project1_db",
    connect_args={"password": "Somi@2005"}
)

print("Connection Successful ✅\n")

# Show tables
tables = pd.read_sql("SHOW TABLES;", engine)
print("Tables in DB:\n", tables, "\n")

# Load tables
orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)
payments = pd.read_sql("SELECT * FROM payments", engine)
products = pd.read_sql("SELECT * FROM products", engine)
print("All Tables Loaded Successfully ✅\n")

# -----------------------
# 2️⃣ SQL ANALYSIS
# -----------------------

# Late Delivery SQL
late_delivery_sql = pd.read_sql("""
SELECT 
    COUNT(*) AS total_orders,
    COALESCE(SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END), 0) AS late_deliveries
FROM orders;
""", engine)

total_orders_sql = late_delivery_sql['total_orders'][0]
late_orders_sql = late_delivery_sql['late_deliveries'][0]
late_percentage_sql = round((late_orders_sql / total_orders_sql) * 100, 2) if total_orders_sql != 0 else 0

print("Late Delivery SQL Output:\n", late_delivery_sql)
print("Late Delivery Percentage (SQL):", late_percentage_sql, "%\n")

# Total Revenue
total_revenue_sql = pd.read_sql("SELECT SUM(price) AS total_revenue FROM order_items;", engine)
print("Total Revenue (SQL):\n", total_revenue_sql, "\n")

# Year-wise Revenue
yearly_revenue_sql = pd.read_sql("""
SELECT YEAR(o.order_purchase_timestamp) AS purchase_year,
       SUM(oi.price) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY YEAR(o.order_purchase_timestamp);
""", engine)
print("Year-wise Revenue (SQL):\n", yearly_revenue_sql, "\n")

# Payment Type Distribution
payment_type_sql = pd.read_sql("""
SELECT payment_type, COUNT(*) AS count
FROM payments
GROUP BY payment_type
ORDER BY count DESC;
""", engine)
print("Payment Type Distribution (SQL):\n", payment_type_sql, "\n")

# -----------------------
# 3️⃣ CSV ANALYSIS (Python)
# -----------------------
# Load CSVs
orders_csv = pd.read_csv(r"C:/Users/Dell/Desktop/Olist data ana project/olist_orders_dataset.csv")
customers_csv = pd.read_csv(r"C:/Users/Dell/Desktop/Olist data ana project/olist_customers_dataset.csv")
items_csv = pd.read_csv(r"C:/Users/Dell/Desktop/Olist data ana project/olist_order_items_dataset.csv")
products_csv = pd.read_csv(r"C:/Users/Dell/Desktop/Olist data ana project/olist_products_dataset.csv")
payments_csv = pd.read_csv(r"C:/Users/Dell/Desktop/Olist data ana project/olist_order_payments_dataset.csv")

print("All CSV files loaded successfully ✅\n")

print(orders.shape)    #count no of rows and col 
print(orders.columns)    #to know col names
print(orders.info())     #to check data types
print(orders.isnull().sum())   #to check missing values

# Convert timestamps
orders_csv['order_purchase_timestamp'] = pd.to_datetime(orders_csv['order_purchase_timestamp'])
orders_csv['order_delivered_customer_date'] = pd.to_datetime(
    orders_csv['order_delivered_customer_date'], errors='coerce'
)
orders_csv['order_estimated_delivery_date'] = pd.to_datetime(
    orders_csv['order_estimated_delivery_date'], errors='coerce'
)

# Add year and month
orders_csv['year'] = orders_csv['order_purchase_timestamp'].dt.year
orders_csv['month'] = orders_csv['order_purchase_timestamp'].dt.month

# Check missing values
print("Missing values per column:\n", orders_csv.isnull().sum(), "\n")

# Monthly Orders
monthly_orders = orders_csv.groupby('month')['order_id'].count()
monthly_orders.plot(kind='bar', title="Monthly Orders", xlabel="Month", ylabel="Number of Orders")
plt.show()

# Merge orders + items
orders_items_merge = pd.merge(orders_csv, items_csv, on='order_id')

# Total Revenue
total_revenue = orders_items_merge['price'].sum()
print("Total Revenue (Python):", total_revenue, "\n")

# Year-wise Revenue
yearly_revenue = orders_items_merge.groupby('year')['price'].sum()
yearly_revenue.plot(kind='bar', title="Yearly Revenue", xlabel="Year", ylabel="Revenue")
plt.show()

# Payment Type Distribution
payment_type = payments_csv['payment_type'].value_counts()
payment_type.plot(kind='bar', title="Payment Method Distribution", xlabel="Payment Type", ylabel="Count")
plt.show()
top_payment_percent = (payment_type['credit_card'] / payment_type.sum()) * 100
print(round(top_payment_percent, 2))

# Top 10 states by orders
customer_orders = pd.merge(orders_csv, customers_csv, on='customer_id')
state_orders = customer_orders['customer_state'].value_counts().head(10)
state_orders.plot(kind='bar', title="Top 10 States by Orders")
plt.show()

# Delivery Delay
orders_csv['delivery_delay'] = (orders_csv['order_delivered_customer_date'] - 
                                orders_csv['order_estimated_delivery_date']).dt.days
late_orders = orders_csv[orders_csv['delivery_delay'] > 0]
late_percentage = (len(late_orders) / len(orders_csv.dropna(subset=['delivery_delay']))) * 100

print("Late Delivery Percentage (Python):", round(late_percentage, 2), "%\n")

# Describe merged dataset for EDA
print(orders_items_merge.describe(include='all'))
