# Olist E-Commerce Analytics

A multi-table SQL analytics project analyzing Brazilian e-commerce data from [Olist](https://www.olist.com/). This project demonstrates end-to-end data analysis: from raw CSV datasets to a SQLite database, through data cleaning, to interactive dashboard visualizations.

## 📊 Project Overview

This project analyzes **9 interconnected datasets** from Olist's Brazilian marketplace (2016-2018), covering:
- **100K+ orders** across multiple product categories
- **Customer behavior** and geographic distribution
- **Seller performance** and delivery metrics
- **Payment patterns** and review sentiment

## 🏗️ Architecture

```
Raw CSVs (data/) → SQLite (olist.db) → Cleaned Exports (dashboard_data/) → Streamlit Dashboard (App.py)
```

### Data Pipeline

| Stage | Script | Description |
|-------|--------|-------------|
| **Ingest** | `Olist cleaning.py` | Load 9 CSV files into SQLite with proper schemas |
| **Clean** | `Olist cleaning.py` | Handle missing values, fix data types, normalize categories |
| **Export** | `export_data.py` | Generate aggregated CSV views for dashboarding |
| **Visualize** | `App.py` | Interactive Streamlit dashboard |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `App.py` | Streamlit dashboard with multi-page analytics |
| `Olist cleaning.py` | Data ingestion, cleaning, and SQLite creation |
| `export_data.py` | Pre-computed aggregations for fast dashboard loads |
| `dashboard_data/` | Ready-to-plot CSV exports (committed for portability) |
| `Requirements.txt` | Python dependencies |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Sadiraja/olist-ecommerce-analytics.git
cd olist-ecommerce-analytics

# Install dependencies
pip install -r Requirements.txt

# Run the dashboard
streamlit run App.py
```

> **Note**: The raw CSV files in `data/` and the SQLite database `olist.db` are **not committed** (too large). On first run, place the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) CSVs in `data/`, then run `Olist cleaning.py` to generate `olist.db`, followed by `export_data.py` to create dashboard exports.

## 📈 Dashboard Features

- **Executive Summary** — KPIs: revenue, orders, customers, AOV
- **Sales Trends** — Monthly revenue, orders, and growth rates
- **Geographic Analysis** — State-level heatmaps and city rankings
- **Category Performance** — Top categories by revenue, volume, margin
- **Delivery Analytics** — Shipping times, delays, carrier performance
- **Customer Behavior** — Repeat purchase rates, RFM segmentation
- **Seller Leaderboard** — Top sellers by volume, rating, speed

## 🔬 Sample Queries

The project includes 20+ analytical SQL queries covering:

```sql
-- Monthly revenue trend
SELECT strftime('%Y-%m', order_purchase_timestamp) AS month,
       SUM(price + freight_value) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE order_status = 'delivered'
GROUP BY month
ORDER BY month;

-- Repeat customer rate
SELECT 
  COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 1.0 / 
  COUNT(DISTINCT customer_id) AS repeat_rate
FROM (
  SELECT customer_id, COUNT(*) AS order_count
  FROM orders
  WHERE order_status = 'delivered'
  GROUP BY customer_id
);
```

## 🌐 Live Demo

**[👉 View Live Dashboard](https://olist-ecommerce-analytics-uw7ndepz2ram6q3beq5jla.streamlit.app/)**

> *Deployed on Streamlit Community Cloud. Data refreshes monthly.*

---

## 📚 Dataset Reference

| Dataset | Rows | Description |
|---------|------|-------------|
| `olist_customers_dataset.csv` | ~99K | Customer info + geolocation |
| `olist_orders_dataset.csv` | ~100K | Order timestamps, status |
| `olist_order_items_dataset.csv` | ~112K | Order line items |
| `olist_order_payments_dataset.csv` | ~103K | Payment methods, installments |
| `olist_order_reviews_dataset.csv` | ~99K | Review scores, comments |
| `olist_products_dataset.csv` | ~33K | Product details, categories |
| `olist_sellers_dataset.csv` | ~3K | Seller info + geolocation |
| `olist_geolocation_dataset.csv` | ~1M | Brazilian zip code coordinates |
| `product_category_name_translation.csv` | 71 | Portuguese → English categories |

## 🛠️ Tech Stack

- **Python 3.9+**
- **pandas** — data manipulation
- **SQLite** — embedded analytical database
- **Streamlit** — interactive web dashboard
- **Plotly** — interactive visualizations

## 📄 License

MIT License — feel free to use for learning or portfolio projects.

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-viz`)
3. Commit changes (`git commit -m 'Add amazing visualization'`)
4. Push to branch (`git push origin feature/amazing-viz`)
5. Open a Pull Request

---

**Built with ❤️ for learning multi-table SQL analytics**
