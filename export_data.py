"""Runs the analysis SQL against olist.db and saves small result tables as CSVs.
The dashboard reads these CSVs, so the big database never has to be deployed."""
import os
import sqlite3
import pandas as pd

DB_PATH = "olist.db"
OUT_DIR = "dashboard_data"
os.makedirs(OUT_DIR, exist_ok=True)

QUERIES = {
    # revenue by month and customer state
    "monthly_state": """
        SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
               c.customer_state,
               ROUND(SUM(oi.price), 2) AS revenue,
               COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY month, c.customer_state
    """,
    # revenue by product category, month and state
    "category_month_state": """
        SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
               c.customer_state,
               COALESCE(t.product_category_name_english,
                        p.product_category_name, 'unknown') AS category,
               ROUND(SUM(oi.price), 2) AS revenue
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
               ON p.product_category_name = t.product_category_name
        WHERE o.order_status = 'delivered'
        GROUP BY month, c.customer_state, category
    """,
    # late vs on-time deliveries and review scores
    "delivery_month_state": """
        SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS month,
               c.customer_state,
               CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
                    THEN 'Late' ELSE 'On time' END AS delivery,
               COUNT(*) AS orders,
               SUM(r.review_score) AS review_sum
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_status = 'delivered'
          AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY month, c.customer_state, delivery
    """,
    # repeat customers (uses customer_unique_id, not customer_id)
    "repeat_overall": """
        WITH cust AS (
            SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        )
        SELECT COUNT(*) AS customers,
               SUM(CASE WHEN n_orders > 1 THEN 1 ELSE 0 END) AS repeat_customers
        FROM cust
    """,
}

conn = sqlite3.connect(DB_PATH)
for name, sql in QUERIES.items():
    df = pd.read_sql_query(sql, conn)
    df.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: {len(df):,} rows")
conn.close()