import os
import sqlite3
import pandas as pd

DATA = "data"          # folder containing the extracted Kaggle CSVs
DB_PATH = "olist.db"


def read(name):
    return pd.read_csv(os.path.join(DATA, name))


# ---------- ORDERS: parse date columns ----------
orders = read("olist_orders_dataset.csv")
date_cols = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
for c in date_cols:
    orders[c] = pd.to_datetime(orders[c], errors="coerce")

# Check: deliveries dated before purchase (logical errors). Flag, don't silently drop.
bad_dates = orders[
    orders["order_delivered_customer_date"] < orders["order_purchase_timestamp"]
]
print(f"Orders delivered before purchase date: {len(bad_dates)}")

# ---------- REVIEWS: keep only the latest review per order ----------
reviews = read("olist_order_reviews_dataset.csv")
reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"], errors="coerce"
)
before = len(reviews)
reviews = reviews.sort_values("review_answer_timestamp").drop_duplicates(
    "order_id", keep="last"
)
print(f"Reviews: removed {before - len(reviews)} duplicate rows (kept latest per order)")

# ---------- CATEGORY TRANSLATION: add the 2 missing categories ----------
trans = read("product_category_name_translation.csv")
extra = pd.DataFrame(
    {
        "product_category_name": [
            "pc_gamer",
            "portateis_cozinha_e_preparadores_de_alimentos",
        ],
        "product_category_name_english": [
            "pc_gamer",
            "portable_kitchen_food_preparers",
        ],
    }
)
trans = pd.concat([trans, extra], ignore_index=True).drop_duplicates(
    "product_category_name"
)

# ---------- TABLES THAT NEED NO CHANGES ----------
items = read("olist_order_items_dataset.csv")
customers = read("olist_customers_dataset.csv")
products = read("olist_products_dataset.csv")
sellers = read("olist_sellers_dataset.csv")
payments = read("olist_order_payments_dataset.csv")

# ---------- LOAD INTO SQLITE ----------
conn = sqlite3.connect(DB_PATH)
tables = {
    "orders": orders,
    "order_items": items,
    "customers": customers,
    "order_reviews": reviews,
    "products": products,
    "sellers": sellers,
    "order_payments": payments,
    "product_category_name_translation": trans,
}
for name, frame in tables.items():
    frame.to_sql(name, conn, if_exists="replace", index=False)
    print(f"Loaded {name}: {len(frame):,} rows")
conn.close()
print(f"Done -> {DB_PATH}")