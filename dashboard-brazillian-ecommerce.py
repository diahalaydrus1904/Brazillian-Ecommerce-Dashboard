import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import plotly.express as px
import json
import urllib.request

@st.cache_data
def load_brazil_geojson():
    url = (
        "https://raw.githubusercontent.com/codeforamerica/"
        "click_that_hood/master/public/data/brazil-states.geojson"
    )
    with urllib.request.urlopen(url) as response:
        geojson = json.load(response)
    return geojson


sns.set(style="darkgrid")

@st.cache_data
def load_data():
    # LOAD RAW CSV FILES
    orders_df = pd.read_csv("data/orders_dataset.csv")
    order_items_df = pd.read_csv("data/order_items_dataset.csv")
    order_payments_df = pd.read_csv("data/order_payments_dataset.csv")
    order_reviews_df = pd.read_csv("data/order_reviews_dataset.csv")
    customers_df = pd.read_csv("data/customers_dataset.csv")
    products_df = pd.read_csv("data/products_dataset.csv")
    sellers_df = pd.read_csv("data/sellers_dataset.csv")
    category_df = pd.read_csv("data/product_category_name_translation.csv")

    # DATETIME CONVERSION
    datetime_cols = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_approved_at",
        "order_delivered_carrier_date"
    ]

    for col in datetime_cols:
        if col in orders_df.columns:
            orders_df[col] = pd.to_datetime(orders_df[col], errors="coerce")

    # MERGE PROCESS

    # orders + customers
    all_df = orders_df.merge(
        customers_df,
        on="customer_id",
        how="left"
    )

    # + order items
    all_df = all_df.merge(
        order_items_df,
        on="order_id",
        how="inner"
    )

    # + payments
    all_df = all_df.merge(
        order_payments_df,
        on="order_id",
        how="left"
    )

    # + reviews
    all_df = all_df.merge(
        order_reviews_df,
        on="order_id",
        how="left"
    )

    # + products
    all_df = all_df.merge(
        products_df,
        on="product_id",
        how="left"
    )

    # + category translation
    all_df = all_df.merge(
        category_df,
        on="product_category_name",
        how="left"
    )

    # + sellers
    all_df = all_df.merge(
        sellers_df,
        on="seller_id",
        how="left"
    )


    # FEATURE ENGINEERING
    all_df["revenue"] = all_df["price"] + all_df["freight_value"]

    return all_df

all_df = load_data()
brazil_geojson = load_brazil_geojson()

# SIDEBAR FILTER
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/0/05/Flag_of_Brazil.svg",
    width=200
)

min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Order Date Range",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

filtered_df = all_df[
    (all_df["order_purchase_timestamp"].dt.date >= start_date) &
    (all_df["order_purchase_timestamp"].dt.date <= end_date)
]

# HELPER FUNCTIONS
def monthly_revenue(df):
    monthly = (
        df.resample("ME", on="order_purchase_timestamp")
          .agg(total_revenue=("payment_value", "sum"),
               total_orders=("order_id", "nunique"))
          .reset_index()
    )
    return monthly

def category_revenue(df):
    df["revenue"] = df["price"] + df["freight_value"]
    return (
        df.groupby("product_category_name_english", as_index=False)
          .agg(total_revenue=("revenue", "sum"))
          .sort_values("total_revenue", ascending=False)
    )

def customers_by_state(df):
    return (
        df.groupby("customer_state", as_index=False)
          .agg(total_customers=("customer_unique_id", "nunique"))
          .sort_values("total_customers", ascending=False)
    )

def delivery_time(df):
    df = df.dropna(subset=["order_delivered_customer_date"])
    df["delivery_days"] = (
        df["order_delivered_customer_date"] -
        df["order_purchase_timestamp"]
    ).dt.days
    return df[df["delivery_days"] >= 0]

def delivery_analysis(df):
    delivery_df = df.dropna(
        subset=["order_delivered_customer_date", "order_purchase_timestamp"]
    ).copy()

    delivery_df["delivery_days"] = (
        delivery_df["order_delivered_customer_date"] -
        delivery_df["order_purchase_timestamp"]
    ).dt.days

    delivery_df = delivery_df[delivery_df["delivery_days"] >= 0]

    avg_delivery_time = delivery_df["delivery_days"].mean()

    delivery_by_state = (
        delivery_df.groupby("customer_state", as_index=False)
        .agg(
            avg_delivery_time=("delivery_days", "mean"),
            total_orders=("order_id", "nunique")
        )
        .sort_values("avg_delivery_time", ascending=False)
    )

    return avg_delivery_time, delivery_by_state

def seller_revenue(df):
    df["revenue"] = df["price"] + df["freight_value"]
    return (
        df.groupby("seller_id", as_index=False)
          .agg(total_revenue=("revenue", "sum"))
          .sort_values("total_revenue", ascending=False)
    )

def review_by_category(df):
    return (
        df.groupby("product_category_name_english", as_index=False)
          .agg(
              avg_review_score=("review_score", "mean"),
              total_reviews=("review_score", "count")
          )
          .query("total_reviews >= 50")
          .sort_values("avg_review_score", ascending=False)
    )

def rfm_summary(df):
    rfm = (
        df.groupby("customer_unique_id", as_index=False)
          .agg(
              last_order=("order_purchase_timestamp", "max"),
              frequency=("order_id", "nunique"),
              monetary=("payment_value", "sum")
          )
    )
    recent_date = df["order_purchase_timestamp"].max()
    rfm["recency"] = (recent_date - rfm["last_order"]).dt.days
    return rfm.drop(columns="last_order")

def create_rfm_df(df):
    rfm_df = (
        df.groupby("customer_unique_id", as_index=False)
          .agg(
              last_order=("order_purchase_timestamp", "max"),
              frequency=("order_id", "nunique"),
              monetary=("payment_value", "sum")
          )
    )

    recent_datetime = df["order_purchase_timestamp"].max()

    rfm_df["recency_days"] = (
        (recent_datetime - rfm_df["last_order"]).dt.days
    )

    rfm_df.drop(columns="last_order", inplace=True)
    return rfm_df

# DASHBOARD HEADER
st.title("Brazilian E-Commerce Dashboard")
st.caption("Exploratory & Business Insight Dashboard")

st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <style>
    .sidebar-footer {
        font-size: 13px;
        color: #6b7280; /* gray-500 */
        text-align: center;
        line-height: 1.6;
    }
    .sidebar-footer a {
        color: #374151; /* gray-700 */
        text-decoration: none;
        margin: 0 6px;
        font-weight: 500;
    }
    .sidebar-footer a:hover {
        text-decoration: underline;
    }
    </style>

    <div class="sidebar-footer">
        <div>Built By</div>
        <div><strong>Rodiah Hasan Alaydrus</strong></div>
        <div>
            <a href="https://www.linkedin.com/in/rodiah-hasan-alaydrus-65571a262/" target="_blank">LinkedIn</a> ·
            <a href="https://github.com/diahalaydrus1904" target="_blank">GitHub</a> ·
            <a href="mailto:diahalaydrus1904@gmail.com">Email</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# KPI METRICS
monthly_df = monthly_revenue(filtered_df)

col1, col2 = st.columns(2)
col1.metric("Total Orders", monthly_df.total_orders.sum())
col2.metric(
    "Average Monthly Revenue",
    format_currency(monthly_df.total_revenue.mean(), "BRL", locale="pt_BR")
)

# MONTHLY REVENUE TREND
st.subheader("Monthly Revenue Trend")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(
    monthly_df["order_purchase_timestamp"],
    monthly_df["total_revenue"],
    marker="o"
)
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (BRL)")
st.pyplot(fig)

# PRODUCT CATEGORY PERFORMANCE
st.subheader("Product Category Performance")

cat_rev = category_revenue(filtered_df)

fig, ax = plt.subplots(ncols=2, figsize=(18, 7))

sns.barplot(
    data=cat_rev.head(5),
    x="total_revenue",
    y="product_category_name_english",
    ax=ax[0]
)
ax[0].set_title("Top 5 Revenue Categories")

bottom_categories = (
    cat_rev.tail(5)
    .sort_values("total_revenue", ascending=True)
    .head(5)
)

sns.barplot(
    data=bottom_categories,
    x="total_revenue",
    y="product_category_name_english",
    ax=ax[1]
)

# THIS IS THE KEY PART
ax[1].invert_xaxis()

ax[1].set_title("Lowest 5 Revenue Categories")
ax[1].set_xlabel("Total Revenue")
ax[1].set_ylabel("")

plt.tight_layout()
plt.subplots_adjust(wspace=0.6)


st.pyplot(fig)

# CUSTOMERS BY STATE
st.subheader("Customer Distribution by State")

state_df = customers_by_state(filtered_df)

fig = px.choropleth(
    state_df,
    geojson=brazil_geojson,
    locations="customer_state",       
    featureidkey="properties.sigla",   
    color="total_customers",
    color_continuous_scale="Blues",
    labels={
        "total_customers": "Total Customers",
        "customer_state": "State"
    }
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)

# DELIVERY TIME VS REVIEW SCORE
st.subheader("Delivery Time vs Review Score")

delivery_df = delivery_time(filtered_df)

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=delivery_df,
    x="delivery_days",
    y="review_score",
    alpha=0.4,
    ax=ax
)
ax.set_xlabel("Delivery Time (Days)")
ax.set_ylabel("Review Score")
st.pyplot(fig)

# DELIVERY TIME ANALYSIS
st.subheader("Delivery Time Analysis")

avg_delivery_time, delivery_by_state = delivery_analysis(filtered_df)

# KPI 
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Average Delivery Time (Days)",
        round(avg_delivery_time, 2)
    )

with col2:
    st.metric(
        "State with Longest Avg Delivery",
        delivery_by_state.iloc[0]["customer_state"]
    )


# BRAZIL MAP — DELIVERY TIME
st.subheader("Average Delivery Time by State")

fig = px.choropleth(
    delivery_by_state,
    geojson=brazil_geojson,
    locations="customer_state",  
    featureidkey="properties.sigla", 
    color="avg_delivery_time",
    color_continuous_scale="Blues",
    labels={
        "avg_delivery_time": "Avg Delivery Time (Days)",
        "customer_state": "State"
    }
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)

# TOP SELLERS
st.subheader("Top Sellers by Revenue")

seller_df = seller_revenue(filtered_df)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=seller_df.head(10),
    x="total_revenue",
    y="seller_id",
    ax=ax
)
ax.set_title("Top 10 Sellers")
st.pyplot(fig)

# REVIEW SCORE BY CATEGORY
st.subheader("Product Review Performance")

review_cat = review_by_category(filtered_df)

fig, ax = plt.subplots(ncols=2, figsize=(18, 7))

# HIGHEST RATED CATEGORIES
top_categories = (
    review_cat.head(5)
    .sort_values("avg_review_score", ascending=False)
    .head(5)
)

sns.barplot(
    data=top_categories,
    x="avg_review_score",
    y="product_category_name_english",
    ax=ax[0]
)

ax[0].set_title("Highest Rated Categories")
ax[0].set_xlabel("Average Review Score")
ax[0].set_ylabel("Product Category")
ax[0].set_xlim(0, 5)

# LOWEST RATED CATEGORIES
bottom_categories = (
    review_cat.tail(5)
    .sort_values("avg_review_score", ascending=True)
    .head(5)
)

sns.barplot(
    data=bottom_categories,
    x="avg_review_score",
    y="product_category_name_english",
    ax=ax[1]
)

ax[1].invert_xaxis()

ax[1].set_title("Lowest Rated Categories")
ax[1].set_xlabel("Average Review Score")
ax[1].set_ylabel("")
ax[1].set_xlim(5, 0)

# LAYOUT FIX
plt.tight_layout()
plt.subplots_adjust(wspace=0.6)

st.pyplot(fig)

# RFM SUMMARY
st.subheader("RFM Customer Summary")

rfm_df = create_rfm_df(filtered_df)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Avg Recency (days)",
        round(rfm_df["recency_days"].mean(), 1)
    )

with col2:
    st.metric(
        "Avg Frequency",
        round(rfm_df["frequency"].mean(), 2)
    )

with col3:
    st.metric(
        "Avg Monetary",
        format_currency(
            rfm_df["monetary"].mean(),
            "BRL",
            locale="pt_BR"
        )
    )

# RFM VISUALIZATION
st.subheader("Top Customers Based on RFM Analysis")

rfm_hours_df = create_rfm_df(filtered_df)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

# Recency
sns.barplot(
    data=rfm_df.sort_values("recency_days").head(5),
    x="customer_unique_id",
    y="recency_days",
    ax=ax[0]
)
ax[0].set_title("Top Customers by Recency (Days)")
ax[0].set_xlabel("Customer ID")
ax[0].set_ylabel("Days Since Last Purchase")
ax[0].tick_params(axis='x', rotation=45)

# Frequency
sns.barplot(
    data=rfm_df.sort_values("frequency", ascending=False).head(5),
    x="customer_unique_id",
    y="frequency",
    ax=ax[1]
)
ax[1].set_title("Top Customers by Frequency")
ax[1].set_xlabel("Customer ID")
ax[1].set_ylabel("Number of Orders")
ax[1].tick_params(axis='x', rotation=45)

# Monetary
sns.barplot(
    data=rfm_df.sort_values("monetary", ascending=False).head(5),
    x="customer_unique_id",
    y="monetary",
    ax=ax[2]
)
ax[2].set_title("Top Customers by Monetary Value")
ax[2].set_xlabel("Customer ID")
ax[2].set_ylabel("Total Revenue (BRL)")
ax[2].tick_params(axis='x', rotation=45)

st.pyplot(fig)

st.markdown(
    '© Brazilian E-Commerce Data Analysis | '
    '<a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce" target="_blank">'
    'Olist Dataset</a> | '
    'Built by Rodiah Hasan Alaydrus',
    unsafe_allow_html=True
)

