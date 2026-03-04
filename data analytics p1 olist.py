import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# -----------------------
# 1️⃣ MySQL CONNECTION
# -----------------------
import urllib.parse

password = urllib.parse.quote_plus("Somi@2005")

engine = create_engine(
    f"mysql+mysqlconnector://root:{password}@localhost/project1_db"
)
print("Connection Successful ✅\n")

# -----------------------
# 2️⃣ LOAD TABLES
# -----------------------
orders = pd.read_sql("SELECT * FROM orders", engine)
order_items = pd.read_sql("SELECT * FROM order_items", engine)
customers = pd.read_sql("SELECT * FROM customers", engine)
payments = pd.read_sql("SELECT * FROM payments", engine)

print("All Tables Loaded Successfully ✅\n")

# -----------------------
# 3️⃣ SQL ANALYSIS
# -----------------------

# Late Delivery
late_sql = pd.read_sql("""
SELECT 
    COUNT(*) AS total_orders,
    SUM(order_delivered_customer_date > order_estimated_delivery_date) AS late_orders
FROM orders;
""", engine)

total = late_sql.loc[0, "total_orders"]
late = late_sql.loc[0, "late_orders"] or 0
late_percent = round((late / total) * 100, 2) if total else 0

print("Late Delivery % (SQL):", late_percent)

# Total Revenue
revenue_sql = pd.read_sql("SELECT SUM(price) AS total_revenue FROM order_items;", engine)
print("Total Revenue (SQL):", revenue_sql.loc[0, "total_revenue"])

# Year-wise Revenue
yearly_sql = pd.read_sql("""
SELECT YEAR(o.order_purchase_timestamp) AS year,
       SUM(oi.price) AS revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY year;
""", engine)

print("\nYearly Revenue:\n", yearly_sql)

# Payment Distribution
payment_sql = pd.read_sql("""
SELECT payment_type, COUNT(*) AS count
FROM payments
GROUP BY payment_type
ORDER BY count DESC;
""", engine)

print("\nPayment Distribution:\n", payment_sql)

# -----------------------
# 4️⃣ SAVE FILES FOR POWER BI
# -----------------------
# -----------------------
# 4️⃣ SAVE EVERYTHING IN ONE EXCEL FILE
# -----------------------

output_file = "sales_analysis_report.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    late_sql.to_excel(writer, sheet_name="Late Delivery", index=False)
    revenue_sql.to_excel(writer, sheet_name="Total Revenue", index=False)
    yearly_sql.to_excel(writer, sheet_name="Yearly Revenue", index=False)
    payment_sql.to_excel(writer, sheet_name="Payment Distribution", index=False)

print("\nAll analysis saved into one Excel file successfully ✅")
