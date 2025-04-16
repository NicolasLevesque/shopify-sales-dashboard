import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
from scripts.predictive_analytics.sales_forecast import generate_forecast_plot
import datetime

# Load environment variables
load_dotenv()

USE_REAL_SHOPIFY_DATA = os.getenv("USE_REAL_SHOPIFY_DATA", "False").lower() == "true"

# Database connection parameters (from .env)
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "airflow")
DB_USER = os.getenv("POSTGRES_USER", "airflow")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "airflow")
DB_PORT = int(os.getenv("POSTGRES_PORT", 5432))


# Load data with caching and clear toggle logic
@st.cache_data(ttl=600)
def load_data():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

    table_name = "real_orders" if USE_REAL_SHOPIFY_DATA else "synthetic_orders"
    df = pd.read_sql(
        f"SELECT * FROM {table_name} WHERE order_date::date <= CURRENT_DATE", conn
    )
    conn.close()
    return df


def main():
    st.cache_data.clear()

    # Set page configuration for better layout
    st.set_page_config(page_title="Shopify Sales Dashboard", layout="wide")
    st.title("📈 Shopify Sales Dashboard")

    # Load the Shopify sales data
    df = load_data()
    if df.empty:
        st.warning("No data available.")
        return

    # Ensure order_date column is in datetime format
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Sidebar filters for interactive data exploration
    min_date, max_date = df["order_date"].min(), df["order_date"].max()

    with st.sidebar:
        st.header("Filter Dashboard")
        # Allow users to filter by date range
        start_date, end_date = st.date_input(
            "Order Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date,
        )
        # Allow users to filter by specific product
        products = ["All"] + sorted(df["product"].dropna().unique().tolist())
        selected_product = st.selectbox("Product", products)

    # Filter dataframe based on user input
    filtered_df = df[
        (df["order_date"].dt.date >= start_date)
        & (df["order_date"].dt.date <= end_date)
    ]

    if selected_product != "All":
        filtered_df = filtered_df[filtered_df["product"] == selected_product]

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # Calculate key performance metrics
    total_orders = filtered_df["order_id"].nunique()
    total_revenue = filtered_df["total_price"].sum()
    avg_order_value = (
        (float(total_revenue) / total_orders)
        if total_orders > 0 and float(total_revenue) > 0
        else 0
    )
    error_rows = (
        filtered_df["is_error"].sum() if "is_error" in filtered_df.columns else 0
    )

    # Display metrics in clearly labeled columns with custom currency formatting
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", f"{total_orders:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")
    col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
    col4.metric("Error Rows", f"{int(error_rows)}")

    # Visualization for daily revenue trends (Interactive Line Chart)
    st.subheader("📅 Daily Revenue")
    filtered_df["order_date"] = pd.to_datetime(filtered_df["order_date"]).dt.floor("D")
    daily_revenue = filtered_df.groupby("order_date", as_index=False)[
        "total_price"
    ].sum()
    daily_revenue["order_date"] = daily_revenue["order_date"].dt.strftime("%Y-%m-%d")

    fig_daily = px.line(
        daily_revenue,
        x="order_date",
        y="total_price",
        markers=True,
        labels={"order_date": "Order Date", "total_price": "Revenue ($)"},
        title="Daily Revenue Over Time",
    )
    fig_daily.update_xaxes(type="category")  # explicitly fixes date display issue
    fig_daily.update_layout(xaxis_title="Order Date", yaxis_title="Revenue ($)")
    st.plotly_chart(fig_daily, use_container_width=True)

    # Visualization for top-performing products (Interactive Bar Chart)
    st.subheader("🏆 Top 5 Products by Revenue")
    top_products = (
        filtered_df.groupby("product", as_index=False)["total_price"]
        .sum()
        .sort_values("total_price", ascending=False)
        .head(5)
    )

    fig_products = px.bar(
        top_products,
        x="product",
        y="total_price",
        color="product",
        labels={"product": "Product", "total_price": "Revenue ($)"},
        text_auto=".2s",
    )
    fig_products.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title="Revenue ($)",
        title={"text": "", "x": 0.5, "xanchor": "center"},
    )
    st.plotly_chart(fig_products, use_container_width=True)

    # Visualization for ratio of new to returning customers (Interactive Pie Chart)
    st.subheader("🔄 Ratio of Returning to New Customers")
    customer_counts = filtered_df["customer_type"].value_counts().reset_index()
    customer_counts.columns = ["customer_type", "count"]

    colors = {"New": "#EFFBF8", "Returning": "#8BFDE6"}

    fig_customer_ratio = px.pie(
        customer_counts,
        values="count",
        names="customer_type",
        title="",
        color="customer_type",
        color_discrete_map=colors,
        hole=0,
    )

    fig_customer_ratio.update_layout(
        showlegend=False,  # removes the legend
        uniformtext_minsize=12,  # ensures text remains readable
        uniformtext_mode="hide",  # hides text if it's too small
        margin=dict(t=50, b=50, l=25, r=25),  # adjust margins to enlarge chart
    )

    fig_customer_ratio.update_traces(
        textinfo="percent+label",
        textfont_size=18,
        insidetextorientation="horizontal",
        textposition="auto",
    )
    st.plotly_chart(fig_customer_ratio, use_container_width=True)

    # Most Valuable Customers (High CLV)
    st.subheader("💎 Most Valuable Customers (High CLV)")
    top_customers = (
        filtered_df.groupby(
            ["customer_first_name", "customer_last_name"], as_index=False
        )["total_price"]
        .sum()
        .assign(
            customer_full_name=lambda df: df["customer_first_name"]
            + " "
            + df["customer_last_name"]
        )
        .sort_values("total_price", ascending=False)
        .head(25)
    )

    fig_customers = px.bar(
        top_customers[::-1],  # reverse order for horizontal bar
        x="total_price",
        y="customer_full_name",
        orientation="h",
        labels={
            "customer_full_name": "Customer Name",
            "total_price": "Total Revenue ($)",
        },
        color="total_price",  # Color based on revenue
        color_continuous_scale=["#26EAFC", "#1C5CD7"],  # Gradient from low to high
        title=None,
        text_auto=".2s",
        height=600,
    )

    fig_customers.update_layout(
        coloraxis_showscale=False,
        yaxis=dict(title=None, tickfont=dict(size=14)),  # Adjust the size as needed
        xaxis=dict(
            title=dict(text="Total Revenue ($)", font=dict(size=14)),
            tickfont=dict(size=14),
        ),
        showlegend=False,
    )

    st.plotly_chart(fig_customers, use_container_width=True)

    # Weekly Revenue Trends by Product Over Time
    st.subheader("📅 Weekly Revenue Trends by Product Over Time")
    # Convert order_date to weekly periods (simplified format)
    filtered_df["Week"] = (
        filtered_df["order_date"]
        .dt.to_period("W")
        .apply(lambda r: r.start_time.strftime("%Y-%m-%d"))
    )

    weekly_product_revenue = filtered_df.groupby(["Week", "product"], as_index=False)[
        "total_price"
    ].sum()

    products = weekly_product_revenue["product"].unique()
    color_map = px.colors.qualitative.Alphabet  # or any other Plotly palette
    color_discrete_map = {
        product: color_map[i % len(color_map)] for i, product in enumerate(products)
    }

    # Plot line chart
    fig_revenue_trends = px.line(
        weekly_product_revenue,
        x="Week",
        y="total_price",
        color="product",
        markers=True,
        labels={
            "Date": "Date",
            "total_price": "Total Revenue ($)",
            "product": "Product",
        },
        title="Weekly Revenue Trends by Product Over Time",
        color_discrete_map=color_discrete_map,
    )

    fig_revenue_trends.update_layout(
        yaxis=dict(title="Total Revenue ($)"),
        xaxis=dict(title=None),
        legend_title="Product",
    )

    st.plotly_chart(fig_revenue_trends, use_container_width=True)

    # Do Higher Discounts Lead to Higher Sales?
    st.subheader("🏷️ Do Higher Discounts Lead to Higher Sales?")

    # Scatter plot with gradient color and trend line
    fig_discounts = px.scatter(
        filtered_df.groupby("product", as_index=False).agg(
            {"total_discounts": "sum", "total_price": "sum"}
        ),
        x="total_discounts",
        y="total_price",
        color="total_discounts",
        color_continuous_scale=["#48CAE4", "#023E8A"],
        trendline="ols",
        trendline_color_override="#7A5195",
        labels={
            "total_discounts": "Discount Amount ($)",
            "total_price": "Total Sales ($)",
        },
        hover_name="product",
        title="Do Higher Discounts Lead to Higher Sales?",
        text="product",  # This adds labels to each dot
    )

    # Adjust layout to avoid label overlap and improve visibility
    fig_discounts.update_traces(
        textposition="top center", textfont_size=12, marker=dict(size=15)
    )

    st.plotly_chart(fig_discounts, use_container_width=True)

    # Customer Preferences: Shipping Method (Pie Chart)
    st.subheader("🚚 Customer Preferences: Shipping Method")

    shipping_method_counts = filtered_df["shipping_method"].value_counts().reset_index()
    shipping_method_counts.columns = ["shipping_method", "count"]

    fig_shipping = px.pie(
        shipping_method_counts,
        names="shipping_method",
        values="count",
        title="",
        color_discrete_sequence=px.colors.qualitative.Pastel,  # Adjust palette if desired
        hole=0,  # Optional donut-style, adjust or remove if preferred
    )

    fig_shipping.update_traces(
        textinfo="percent+label",
        textfont_size=14,
        insidetextorientation="horizontal",
        textposition="outside",
    )

    fig_shipping.update_layout(
        showlegend=False,
        margin=dict(t=50, b=50, l=25, r=25),
    )

    st.plotly_chart(fig_shipping, use_container_width=True)

    st.subheader("14-Day Sales Forecast")
    forecast_plot = generate_forecast_plot()
    st.pyplot(forecast_plot)

    # Collapsible section for viewing error rows
    if "is_error" in filtered_df.columns and error_rows > 0:
        with st.expander(f"View Error Rows ({int(error_rows)})"):
            st.dataframe(filtered_df[filtered_df["is_error"] == True])

    # User instructions for easy dashboard navigation
    with st.expander("How to Use This Dashboard"):
        st.markdown(
            """
        - **Filters**: Adjust the date range and select specific products using the sidebar.
        - **Metrics**: Review key performance indicators summarized at the top.
        - **Visualizations**: Analyze detailed revenue trends and identify top products.
        - **Errors**: Inspect potential data issues by expanding the 'Error Rows' section.
        """
        )

    # Inform users of automatic updates
    last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    st.caption(
        f"Dashboard last updated: {last_updated} | Updates every 10 minutes automatically."
    )


if __name__ == "__main__":
    main()
