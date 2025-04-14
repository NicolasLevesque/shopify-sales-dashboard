# 🚀 Shopify Sales Dashboard – User Guide

Welcome to your ready-to-use **Shopify Sales Dashboard**!  
Easily analyze and forecast your Shopify store's performance.

---

## 📂 What's Included?

- **`app.py`** – Streamlit dashboard
- **`scripts/predictive_analytics/sales_forecast.py`** – Prophet forecasting script
- **`scripts/fetch_shopify_data.py`** – Shopify data e`traction script
- **`dags/shopify_etl_dag.py`** – Airflow ETL pipeline
- **`Dockerfile`** – Docker setup
- **`docker-compose.yml`** – Docker Compose setup
- **`.env.example`** – Template environment file
- **`requirements.t`t`** – Python dependencies
- **`setup_database.sql`** – Database schema setup script
- **`setup_database.bat`** – Quick-start database setup script

---

## 🚀 Quick Setup Guide

### ✅ Step 1: Clone the Repository

```
git clone https://github.com/NicolasLevesque/shopify-sales-dashboard.git
cd shopify-sales-dashboard/product_package
```

### ✅ Step 2: Configure Environment Variables

- Rename `.env.example` to `.env`.
- Fill out the required Shopify and PostgreSQL credentials.

### ✅ Step 3: Launch Docker Containers (PostgreSQL, Airflow, Streamlit)

```
docker-compose up --build
```

Your services are now running:

- Airflow Dashboard: `http://localhost:8500`
- Streamlit Dashboard: `http://localhost:8501`

### ✅ Step 4: Set Up Database Schema

- Double-click to run:

```
setup_database.bat
```

This sets up the database schema automatically.

### ✅ Step 5: Run ETL Pipeline with Airflow

- Open Airflow: `http://localhost:8500`
- Trigger the DAG:

```
daily_real_shopify_data
```

This populates the PostgreSQL database.

---

## 📈 Using Your Dashboard

- View live Shopify analytics
- Interact with sales visualizations
- See automated 14-day Prophet forecasts
- Filter by dates and products easily

---

## 🛠 Troubleshooting

- **Docker issues?**  
  Ensure Docker is installed and running.

- **Database connection errors?**  
  Confirm your database credentials in the `.env` file.

- **Empty dashboard or no data?**  
  Check if Airflow DAG ran successfully.

Contact support at:  
`levesquenicolas95@gmail.com`

---

## 📄 License & Terms

This project is licensed under the terms outlined in the [LICENSE.md](LICENSE.md) file.

---

## 🎯 Next Steps

- **Deploy your dashboard publicly:** Heroku, AWS, Streamlit Cloud.
- **Integrate additional Shopify metrics:** Inventory levels, customer lifetime value, or marketing insights.
- **Automate further:** Schedule your DAG for automatic daily Shopify updates.

Enjoy your enhanced Shopify analytics experience!
