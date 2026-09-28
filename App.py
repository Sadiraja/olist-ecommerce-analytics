import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Olist E-Commerce Analytics", layout="wide")
st.title("Olist Brazilian E-Commerce: Business Analytics Dashboard")
st.caption("Delivered orders only. Revenue is item price in Brazilian reais (R$), excluding freight.")


@st.cache_data
def load(name):
    return pd.read_csv(f"dashboard_data/{name}.csv")


monthly = load("monthly_state")
cat = load("category_month_state")
deliv = load("delivery_month_state")
rep = load("repeat_overall")

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
months = sorted(monthly["month"].unique())
start_default = "2017-01" if "2017-01" in months else months[0]
end_default = "2018-08" if "2018-08" in months else months[-1]
m0, m1 = st.sidebar.select_slider(
    "Month range", options=months, value=(start_default, end_default)
)
all_states = sorted(monthly["customer_state"].unique())
states = st.sidebar.multiselect("Customer state (empty = all)", all_states)
st.sidebar.caption(
    "Late 2016 and late 2018 have very few orders, so the default range covers "
    "the full-volume period (2017-01 to 2018-08)."
)


def apply_filters(df):
    d = df[(df["month"] >= m0) & (df["month"] <= m1)]
    if states:
        d = d[d["customer_state"].isin(states)]
    return d


mf = apply_filters(monthly)
cf = apply_filters(cat)
df_ = apply_filters(deliv)

if mf.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---------------- KPI row ----------------
total_rev = mf["revenue"].sum()
total_orders = mf["orders"].sum()
aov = total_rev / total_orders if total_orders else 0
del_orders = df_["orders"].sum()
late_pct = 100 * df_.loc[df_["delivery"] == "Late", "orders"].sum() / del_orders if del_orders else 0
repeat_pct = 100 * rep.loc[0, "repeat_customers"] / rep.loc[0, "customers"]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue", f"R$ {total_rev:,.0f}")
k2.metric("Orders", f"{int(total_orders):,}")
k3.metric("Avg order value", f"R$ {aov:,.0f}")
k4.metric("Late deliveries", f"{late_pct:.1f}%")
k5.metric("Repeat customers*", f"{repeat_pct:.1f}%")
st.caption("*Repeat customer rate is calculated across all states and all dates.")

st.markdown("---")

# ---------------- 1. Monthly revenue ----------------
st.subheader("Monthly revenue and growth")
m = mf.groupby("month", as_index=False)[["revenue", "orders"]].sum()
m["mom_growth_pct"] = (m["revenue"].pct_change() * 100).round(1)
fig1 = px.line(m, x="month", y="revenue", markers=True, title="Revenue by month (R$)")
st.plotly_chart(fig1, use_container_width=True)
with st.expander("Show month-over-month growth table"):
    st.dataframe(m, use_container_width=True)

# ---------------- 2 and 3. Categories / state ----------------
left, right = st.columns(2)

with left:
    st.subheader("Top 10 product categories")
    c = (
        cf.groupby("category", as_index=False)["revenue"].sum()
        .nlargest(10, "revenue").sort_values("revenue")
    )
    fig2 = px.bar(c, x="revenue", y="category", orientation="h",
                  title="Revenue by category (R$)")
    st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader("Top states by revenue")
    s = (
        mf.groupby("customer_state", as_index=False)["revenue"].sum()
        .nlargest(10, "revenue")
    )
    fig3 = px.bar(s, x="customer_state", y="revenue", title="Revenue by state (R$)")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ---------------- 4. Delivery vs review score ----------------
st.subheader("Do late deliveries hurt review scores?")
d = df_.groupby("delivery", as_index=False)[["orders", "review_sum"]].sum()
if d.empty:
    st.info("No delivery data for the selected filters.")
else:
    d["avg_review"] = (d["review_sum"] / d["orders"]).round(2)
    fig4 = px.bar(d, x="delivery", y="avg_review", text="avg_review",
                  title="Average review score (1 to 5)")
    fig4.update_yaxes(range=[0, 5])
    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(d[["delivery", "orders", "avg_review"]], use_container_width=True)