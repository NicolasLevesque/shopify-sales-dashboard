import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

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
        title="Top Products by Revenue",
        text_auto=".2s",
    )
    fig_products.update_layout(
        showlegend=False, xaxis_title="Product", yaxis_title="Revenue ($)"
    )
    st.plotly_chart(fig_products, use_container_width=True)

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
    st.caption("Dashboard updates every 10 minutes automatically.")


if __name__ == "__main__":
    main()
