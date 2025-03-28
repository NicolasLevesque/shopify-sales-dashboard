# Dashboard Features

This document outlines the planned features for our **Shopify Sales Dashboard**, built with **Streamlit** and powered by our Postgres data pipeline.

---

## 1. High-Level Metrics

- **Total Revenue**  
  Summation of the `total` column across all orders.
- **Total Orders**  
  Count of unique `order_id` entries.
- **Average Order Value (AOV)**  
  `Total Revenue / Total Orders`.
- **Number of Error Rows**  
  Count of rows where `is_error = TRUE`.

These metrics give an instant snapshot of sales performance and data quality.

---

## 2. Sales Trend Chart

- **Daily Revenue Over Time**
  - Group by `order_date` and sum `total`.
  - Display as a line chart or bar chart to reveal sales trends.
- (Optional) **Date Range Filter**
  - Let users select a custom time window.

This helps stakeholders see revenue fluctuations and spot patterns quickly.

---

## 3. Error Row Inspection

- **Dedicated Table for Error Rows**
  - Filter `is_error = TRUE`.
  - Show columns like `order_date`, `price`, `quantity`, `shipping_method`, etc.
- **Summary of Issues**
  - Possibly highlight what type of error was triggered (missing price, negative quantity, etc.).

Demonstrates how we handle data anomalies without breaking the main pipeline.

---

## 4. Product or Category Breakdown (Optional)

- **Top Products by Revenue**
  - Group data by product and sum `total`.
  - Bar chart or ranking table for the top 5 products.
- (Optional) **Category-Level View**
  - If categories are simulated, show breakdown by category.

Gives a quick look at what’s selling best in the store.

---

## 5. Filtering & Interactivity (Optional)

- **Date Range Selector**  
  Let users specify a start and end date for the dashboard’s charts.
- **Product/Category Filter**  
  If product or category columns exist, let users refine results further.
- **Hide/Show Errors**  
  A toggle to exclude error rows from the main metrics if desired.

Enhances user experience and real-world application, allowing custom data exploration.

---

## 6. Future Add-Ons

1. **Forecasting**
   - Integrate a simple ML model (Prophet, ARIMA) to predict future revenue.
2. **Anomaly Detection**
   - Highlight unusual revenue spikes/drops or suspicious data in daily trends.
3. **Explanatory Notes**
   - Provide short documentation explaining how data is generated and how errors are injected.

These additions would deepen the dashboard’s analytical power and clarity.

---

## Conclusion

Implementing these features will yield a **comprehensive** Streamlit dashboard, covering essential Shopify metrics, data quality checks, and optional advanced insights. This not only showcases your pipeline’s **ETL capability** but also provides a real-world analytics experience for stakeholders or potential employers to explore.
