# Shopify Sales Dashboard

## Quick Navigation

- [Project Overview](#-project-overview)
- [Quick Start](#-quick-start-instant-usage)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Running the Project](#️-running-the-project)
- [Airflow Automation](#️-airflow-automation)
- [Data Sources & ETL Pipeline](#-data-sources--etl-pipeline)
- [Daily Data Generation](#-daily-data-generation-simulated-shopify-data)
- [Why Choose This Dashboard over Shopify's Built-In Analytics?](#-why-choose-this-dashboard-over-shopifys-built-in-analytics)
- [Note on Analytical Insights & Human Behavior](#-note-on-analytical-insights--human-behavior)
- [Visualizations](#-visualizations)
- [Shopify API Reference](#-shopify-api-reference)
- [Troubleshooting](#️-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [Recent Updates](#-recent-updates)

---

## 🚀 Project Overview

The **Shopify Sales Dashboard** is an automated analytics solution designed specifically for Shopify store owners and analytics enthusiasts. It features a **publicly accessible, continuously updated historical dataset** of realistically generated Shopify sales data. New simulated orders are automatically created and appended daily, enabling an ever-growing dataset ideal for data exploration, visualization, analysis, and machine learning practice.

This open dataset (`shopify_sales.csv`) offers immediate, practical opportunities for:

- 📈 **Sales trend analysis and forecasting**
- 👥 **Customer segmentation and behavioral insights**
- 📊 **Interactive exploratory data analysis**
- ⚙️ **Demonstration of automated data analytics pipelines**

Built around clear automation, scalability, and ease of use, this solution ensures minimal manual intervention and maximum reliability, providing actionable insights through dynamic, interactive dashboards powered by Power BI, Tableau, or Streamlit.

---

## ⚡ Quick Start (Instant Usage)

**Step 1: Get the Data**

```bash
git clone https://github.com/NicolasLevesque/shopify-sales-dashboard.git
cd shopify-sales-dashboard
```

**Step 2: Install Dependencies**

```bash
pip install pandas matplotlib
```

**Step 3: Instantly Run Analyses**

- **Visualize Sales Trends:**

```bash
python quick_visualization.py
```

- **Explore Data Interactively:**

```bash
python explore_data.py
```

- **Forecast Future Sales (Demo):**

```bash
python predict_sales.py
```

---

## 📌 Features

- **Automated Data Extraction:** Real-time Shopify data extraction via Shopify API.
- **Robust ETL Pipeline:** Automated data cleaning & transformation with Python, Pandas, and SQL.
- **Flexible Data Storage:** Supports PostgreSQL and Google BigQuery databases.
- **Scheduled Automation:** ETL processes automated daily using Apache Airflow.
- **Interactive Visualizations:** Dashboards created in Power BI, Tableau, or Streamlit.
- **Email Notifications:** Alerts on ETL pipeline failures via SMTP.
- **Secure Configuration:** Environment variables (no hardcoded credentials).

---

## 🛠️ Tech Stack

- **Programming:** Python, SQL
- **Data Processing:** Pandas, dbt, SQLAlchemy
- **Automation & Scheduling:** Apache Airflow
- **Databases:** PostgreSQL, Google BigQuery
- **Visualization:** Power BI, Tableau, Streamlit
- **API Integration:** Shopify REST API

---

## 📂 Project Structure

- **dags/**: Contains Airflow DAG files for scheduling tasks.
- **scripts/**: Holds ETL Python scripts for data extraction and processing.
- **dashboards/**: Storage location for Power BI/Tableau/Streamlit dashboard files.
- **data/**: Optional storage for raw or intermediate data files.
- **logs/**: Airflow-generated logs (not committed to GitHub).
- **config/**: Contains configuration-related files (e.g., Airflow settings).

---

## 🚧 Getting Started

### Clone the Repository

```bash
git clone https://github.com/NicolasLevesque/shopify-sales-dashboard.git
cd shopify-sales-dashboard
```

### Install Dependencies

Ensure you're using Python 3.8 or later, then run:

```bash
pip install -r requirements.txt
```

> If using Docker, dependencies will be installed automatically by your Docker container.

### Set Up Environment Variables

Copy the `.env.example` file to `.env` in your project root, then update it with your credentials:

```bash
# Shopify Credentials
SHOP_NAME=your-shop-name
ADMIN_ACCESS_TOKEN=your-shopify-access-token

# PostgreSQL Credentials
POSTGRES_DB=shopify_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

> For Docker, you may need to use `POSTGRES_HOST=postgres` or `host.docker.internal`.

---

## ▶️ Running the Project

### Run ETL Manually

To manually run your ETL script (without Airflow):

```bash
python scripts/etl.py
```

Look for the confirmation message `✅ ETL Load Complete` in your console.

Verify data loaded successfully into your database:

```bash
docker exec -it shopify_sales_dashboard-postgres-1 psql -U airflow -d airflow

SELECT * FROM customers LIMIT 5;
SELECT * FROM orders LIMIT 5;
SELECT * FROM products LIMIT 5;
```

### Run ETL with Docker/Airflow

Launch your Docker environment and Airflow scheduler:

```bash
docker-compose up -d
```

Then, access the Airflow UI at [http://localhost:8080](http://localhost:8080), enable your DAG (`daily_shopify_etl`), and trigger it manually or let it run on schedule.

---

## ⚙️ Airflow Automation

### Airflow Setup

1. **Software Dependencies:**

   - Docker & Docker Compose
   - Python (3.8+ recommended)
   - PostgreSQL (Docker-managed or standalone installation)

   Quick installation for Docker: [Install Docker](https://docs.docker.com/get-docker/)

2. **Start Docker Containers:**

   ```bash
   docker-compose up -d
   ```

3. **Verify Docker Containers:**

   ```bash
   docker ps
   ```

4. **Access Airflow Web Interface:**
   - Visit [http://localhost:8080](http://localhost:8080) and enable your DAG (`daily_shopify_etl`).

### Scheduling

- **Default schedule:** Runs daily at midnight (`@daily`).
- **Customize schedule:** Edit the `schedule_interval` parameter in your DAG file (`daily_shopify_etl.py`).

Example (run every 6 hours):

```bash
schedule_interval = '0 */6 * * *'
```

### Email Alerts

Set up email notifications for Airflow task failures:

1. **Configure SMTP settings** in your `.env`:

```bash
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT=587
AIRFLOW__SMTP__SMTP_USER=your_email@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=your_gmail_app_password
AIRFLOW__SMTP__SMTP_MAIL_FROM=your_email@gmail.com
```

2. **Add email settings** to your DAG (`daily_shopify_etl.py`):

```bash
default_args = {
  'email': ['your_email@gmail.com'],
  'email_on_failure': True,
}
```

---

## 📊 Data Sources & ETL Pipeline

**Data Source:**  
The project uses Shopify as its primary data source, leveraging the Shopify REST API to access sales, customer, and product data in real-time.

**ETL Pipeline:**  
The ETL process is managed by `scripts/etl.py`, which extracts data from Shopify, transforms and cleans it using Python and Pandas, and loads it into PostgreSQL.

- **Manual Execution:** Run locally with:

```bash
python scripts/etl.py
```

- **Airflow Automation:**  
  The Airflow DAG (`daily_shopify_etl.py`) automates the ETL pipeline daily at midnight (`@daily`). The DAG runs the ETL script, monitors its success, and sends email notifications upon failure.

You can trigger or monitor the DAG via the Airflow web interface:

- URL: [http://localhost:8080](http://localhost:8080)

---

## 📅 Daily Data Generation (Simulated Shopify Data)

To demonstrate and validate automated analytics capabilities without relying solely on a Shopify test store, the project includes a fully automated, daily-scheduled data generation pipeline using **Apache Airflow** and **Python’s Faker library**.

**What does this mean for the project?**

- Each day, realistic Shopify sales data (including randomized customer names, products, quantities, and pricing) is automatically appended to the dataset (`shopify_sales.csv`).
- The generated data is indistinguishable from typical real-world Shopify data, ensuring a robust demonstration environment for analytics and visualization.

### 🛠️ **How it works:**

- **Airflow DAG:**  
  Located at `dags/generate_shopify_data.py`, this DAG generates daily fake transactions automatically.
- **Data Location:**  
  The generated data is stored at `data/shopify_sales.csv` and seamlessly integrates with existing dashboards for real-time visualization.

### 🔄 **Daily Schedule:**

The default schedule for this data generation is set to run once per day (`@daily`). Customize the schedule by modifying the DAG’s `schedule_interval`.

**Example (run hourly):**

xxxpython
schedule_interval = '@hourly'
xxx

This automation clearly highlights the project’s scalability and real-world applicability, offering a robust demonstration of daily-updated analytics workflows.

---

## 🩺 Data Quality & Failure Simulation

In real-world data pipelines, unexpected issues can arise—such as incomplete rows, invalid dates, or negative quantities. To demonstrate robust data engineering practices, **this project introduces a small chance (~10%) of “bad data”** during daily synthetic order generation:

- **Examples of Induced Errors**:
  - **Missing or Negative Price** – Represents failed calculations or missing fields.
  - **Future Order Date** – Simulates incorrect timestamps or time-zone quirks.
  - **Negative Quantity** – Mimics data entry errors or faulty external integrations.

Each problematic row is marked with a boolean flag, `is_error = TRUE`, so you can easily **isolate** and **remediate** them—mirroring real-world data quality workflows (e.g., quarantining bad records, applying correction scripts, or sending alerts). The pipeline **still runs** seamlessly, showcasing how to handle data anomalies gracefully without halting the entire ETL process.

**Key Takeaways**:

- 💡 **Simulated “failures”** reveal how you might track and fix flawed input.
- ⚙️ **No disruption** to the main pipeline—only flagged rows need cleanup if desired.
- 🔧 **Future Enhancements** can involve an automated “data fix” step or emailing a data quality report.

Check out the `shopify_sales` table (or CSV) to see these _error rows_, each labeled with `is_error`. For details on how these errors are generated, see `generate_shopify_data.py`.

---

## 🎯 **Why Choose This Dashboard over Shopify's Built-In Analytics?**

While Shopify's built-in analytics provides basic metrics, this dashboard delivers advanced, actionable insights designed specifically to grow your business:

- **📊 Advanced Customer Segmentation (RFM Analysis):**\
  Quickly identify your most valuable customers, target them effectively, and predict customer churn before it happens.

- **🚨 Automated Anomaly Detection & Alerts:**\
  Instantly receive email or Slack alerts when unexpected sales drops or spikes occur, helping you respond proactively to changing market conditions.

- **📈 Predictive Analytics & Forecasting:**\
  Powerful forecasting models that predict future sales, inventory requirements, and potential revenue growth opportunities based on historical trends.

- **💡 Interactive & Customizable Dashboards:**\
  Tailor-made, drill-down capable visualizations built in Power BI, Tableau, or Streamlit, enabling you to uncover insights that directly inform strategic decisions.

- **🤖 Completely Hands-Free Automation:**\
  No manual data entry or manual report generation---this dashboard is fully automated from data extraction to daily insights delivery.

---

## 🔍 Note on Analytical Insights & Human Behavior

This dashboard uses synthetic data generated daily for the purpose of demonstrating technical automation, analytics pipelines, and visualization capabilities.

## While effective for showcasing technical processes, synthetic data does not inherently reflect authentic human psychological patterns, motivations, or behaviors. Genuine psychological insights and strategic recommendations require validation and analysis of authentic customer data.

## 📈 Visualizations

The Shopify Sales Dashboard supports visualization through Power BI, Tableau, or Streamlit, allowing you to explore interactive dashboards for deeper business insights.

> **Dashboards coming soon!** _(Dashboard links will be added here when available.)_

---

## 📡 Shopify API Reference

### Authentication & Example API Call

The dashboard uses Shopify's REST API with an admin access token:

```bash
GET https://{SHOP_NAME}.myshopify.com/admin/api/2023-10/orders.json
Headers:
  X-Shopify-Access-Token: {ADMIN_ACCESS_TOKEN}
```

**Python Example:**

```bash
import requests
import os

SHOP_NAME = os.getenv("SHOP_NAME")
ADMIN_ACCESS_TOKEN = os.getenv("ADMIN_ACCESS_TOKEN")

url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-10/orders.json"
headers = {"X-Shopify-Access-Token": ADMIN_ACCESS_TOKEN}

response = requests.get(url, headers=headers)
data = response.json()

print(data)
```

### API Endpoints

The dashboard uses these Shopify API endpoints:

- **Orders:** `/orders.json` (Sales data)
- **Customers:** `/customers.json` (Customer insights)
- **Products:** `/products.json` (Product data & inventory)

All endpoints use the base URL:

```bash
https://{SHOP_NAME}.myshopify.com/admin/api/2023-10/
```

---

## ⚠️ Troubleshooting

**1. PostgreSQL Connection Issues**

- Double-check your `.env` file (`POSTGRES_HOST`, credentials).
- Docker host: use `postgres` or `host.docker.internal`.

**2. Authentication Failed (Shopify API)**

- Verify your `SHOP_NAME` and `ADMIN_ACCESS_TOKEN` in `.env`.

**3. DAG Not Visible in Airflow**

- Ensure the DAG file (`daily_shopify_etl.py`) is in your `dags/` folder.
- Restart your Airflow containers (`docker-compose restart`).

**4. Email Alerts Not Sending**

- Confirm SMTP settings in `.env` and Airflow default_args (`email_on_failure=True`).

---

## 🚧 Future Enhancements

- 🌟 AI-driven sales forecasting
- 📈 Integration with Google Analytics & Stripe
- 🛒 Expand to WooCommerce & Amazon integrations
- 📅 Additional DAGs for parallel tasks or complex workflows
- 📲 Slack notifications for key business events

---

## 📝 Recent Updates

- ✅ **Integrated Apache Airflow** for automated scheduling.
- ✅ Switched to **environment variables** (no hardcoded credentials).
- ✅ Added **email notifications** for ETL pipeline failures.
- ✅ Improved documentation and project structure for clarity.

---
