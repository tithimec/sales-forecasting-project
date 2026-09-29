import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_csv("sales_data.csv")

    df["Date"] = pd.to_datetime(df["Date"])

    return df


@st.cache_data
def load_forecast():

    forecast = pd.read_csv(
        "future_30_day_forecast.csv"
    )

    forecast["Date"] = pd.to_datetime(
        forecast["Date"]
    )

    return forecast


df = load_data()
forecast = load_forecast()

@st.cache_data
def load_test_predictions():

    test_data = pd.read_csv(
        "test_predictions.csv"
    )

    test_data["Date"] = pd.to_datetime(
        test_data["Date"]
    )

    return test_data


test_predictions = load_test_predictions()


# ==========================================
# TITLE
# ==========================================

st.title("📊 Sales Forecasting Dashboard")

st.markdown(
    "### AI-Based Sales Analysis & 30-Day Revenue Forecast"
)

st.markdown("---")


# ==========================================
# KPI CALCULATIONS
# ==========================================

total_revenue = df["Revenue"].sum()

total_quantity = df["Quantity"].sum()

average_daily_revenue = (
    df.groupby("Date")["Revenue"]
    .sum()
    .mean()
)

forecast_revenue = (
    forecast["Predicted_Revenue"]
    .sum()
)


# ==========================================
# KPI CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Total Revenue",
        f"৳{total_revenue:,.0f}"
    )

with col2:

    st.metric(
        "📦 Total Quantity Sold",
        f"{total_quantity:,.0f}"
    )

with col3:

    st.metric(
        "📅 Avg Daily Revenue",
        f"৳{average_daily_revenue:,.0f}"
    )

with col4:

    st.metric(
        "🔮 Next 30 Days Forecast",
        f"৳{forecast_revenue:,.0f}"
    )


st.markdown("---")


# ==========================================
# SIDEBAR FILTER
# ==========================================

st.sidebar.header("🔎 Filters")

selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All"] + sorted(
        df["Category"].unique().tolist()
    )
)

selected_region = st.sidebar.selectbox(
    "Select Region",
    ["All"] + sorted(
        df["Region"].unique().tolist()
    )
)


# ==========================================
# FILTER DATA
# ==========================================

filtered_df = df.copy()

if selected_category != "All":

    filtered_df = filtered_df[
        filtered_df["Category"]
        == selected_category
    ]


if selected_region != "All":

    filtered_df = filtered_df[
        filtered_df["Region"]
        == selected_region
    ]


# ==========================================
# DAILY SALES TREND
# ==========================================

st.subheader("📈 Historical Sales Trend")

daily_sales = (
    filtered_df
    .groupby("Date", as_index=False)["Revenue"]
    .sum()
)

fig_daily = px.line(
    daily_sales,
    x="Date",
    y="Revenue",
    title="Daily Revenue Trend",
    markers=False
)

fig_daily.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue (৳)"
)

st.plotly_chart(
    fig_daily,
    use_container_width=True
)


# ==========================================
# TWO COLUMN SECTION
# ==========================================

col1, col2 = st.columns(2)


# ==========================================
# PRODUCT SALES
# ==========================================

with col1:

    st.subheader("🏆 Revenue by Product")

    product_sales = (
        filtered_df
        .groupby("Product", as_index=False)["Revenue"]
        .sum()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    fig_product = px.bar(
        product_sales,
        x="Revenue",
        y="Product",
        orientation="h",
        title="Product Revenue"
    )

    st.plotly_chart(
        fig_product,
        use_container_width=True
    )


# ==========================================
# CATEGORY SALES
# ==========================================

with col2:

    st.subheader("🛍️ Revenue by Category")

    category_sales = (
        filtered_df
        .groupby(
            "Category",
            as_index=False
        )["Revenue"]
        .sum()
    )

    fig_category = px.pie(
        category_sales,
        values="Revenue",
        names="Category",
        title="Category Revenue Distribution"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ==========================================
# REGION SALES
# ==========================================

st.subheader("🌍 Revenue by Region")

region_sales = (
    filtered_df
    .groupby(
        "Region",
        as_index=False
    )["Revenue"]
    .sum()
    .sort_values(
        "Revenue",
        ascending=False
    )
)

fig_region = px.bar(
    region_sales,
    x="Region",
    y="Revenue",
    title="Regional Revenue"
)

st.plotly_chart(
    fig_region,
    use_container_width=True
)

# ==========================================
# MODEL PERFORMANCE
# ==========================================

st.markdown("---")

st.subheader("🤖 Model Performance")

# Calculate metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error

actual = test_predictions["Revenue"]
predicted = test_predictions["Predicted_Revenue"]

mae = mean_absolute_error(actual, predicted)

rmse = np.sqrt(
    mean_squared_error(actual, predicted)
)

mape = np.mean(
    np.abs((actual - predicted) / actual)
) * 100


# Metric cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "MAE",
        f"৳{mae:,.0f}"
    )

with col2:
    st.metric(
        "RMSE",
        f"৳{rmse:,.0f}"
    )

with col3:
    st.metric(
        "MAPE",
        f"{mape:.2f}%"
    )


# ==========================================
# ACTUAL VS PREDICTED
# ==========================================

st.subheader("📊 Actual vs Predicted Revenue")

fig_performance = px.line(
    test_predictions,
    x="Date",
    y=["Revenue", "Predicted_Revenue"],
    title="Actual vs Predicted Revenue"
)

fig_performance.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue (৳)",
    legend_title="Revenue Type"
)

st.plotly_chart(
    fig_performance,
    use_container_width=True
)

# ==========================================
# 30 DAY FORECAST
# ==========================================

st.markdown("---")

st.subheader(
    "🔮 Next 30 Days Sales Forecast"
)

fig_forecast = px.line(
    forecast,
    x="Date",
    y="Predicted_Revenue",
    title="Predicted Revenue for Next 30 Days",
    markers=True
)

fig_forecast.update_layout(
    xaxis_title="Date",
    yaxis_title="Predicted Revenue (৳)"
)

st.plotly_chart(
    fig_forecast,
    use_container_width=True
)


# ==========================================
# FORECAST TABLE
# ==========================================

st.subheader("📋 Forecast Details")

display_forecast = forecast.copy()

display_forecast["Predicted_Revenue"] = (
    display_forecast[
        "Predicted_Revenue"
    ].round(2)
)

display_forecast.columns = [
    "Date",
    "Predicted Revenue (৳)"
]

st.dataframe(
    display_forecast,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# DOWNLOAD FORECAST
# ==========================================

csv = forecast.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download 30-Day Forecast",
    data=csv,
    file_name="30_day_sales_forecast.csv",
    mime="text/csv"
)


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption(
    "AI-Based Sales Forecasting System | "
    "Built with Python, XGBoost & Streamlit"
)