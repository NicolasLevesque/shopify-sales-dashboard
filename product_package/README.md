# 🚀 Shopify Sales Dashboard – User Guide

Welcome to your ready-to-use **Shopify Sales Dashboard**!  
Effortlessly analyze and forecast your Shopify store's performance.

---

## 📂 What's Included?

- **`app.py`** – Streamlit dashboard
- **`scripts/predictive_analytics/sales_forecast.py`** – Prophet forecasting script
- **`scripts/fetch_shopify_data.py`** – Shopify data extraction script
- **`dags/shopify_etl_dag.py`** – Airflow ETL pipeline
- **`Dockerfile`** – Docker setup
- **`docker-compose.yml`** – Docker Compose setup
- **`.env.example`** – Template environment file
- **`requirements.txt`** – Python dependencies

---

## 🚀 Quick Setup Guide

### ✅ Step 1: Unzip the Package

- Download the Shopify Sales Dashboard ZIP file.
- Unzip it to your chosen location.

### ✅ Step 2: Configure Environment Variables

- Rename `.env.example` to `.env`.
- Fill out your Shopify and PostgreSQL credentials.

### ✅ Step 3: Launch Docker Containers

```bash
docker compose up --build
```

Wait a few minutes until all services are fully initialized.

Your services will be accessible at:

- **Airflow Dashboard**: [http://localhost:8500](http://localhost:8500)
- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
- **pgAdmin (Database Viewer)**: [http://localhost:5050](http://localhost:5050)

_No additional database setup is required—this is handled automatically!_

### ✅ Step 4: Run ETL Pipeline with Airflow

- Open [Airflow](http://localhost:8500).
- Under "DAGs," locate `fetch_shopify_data`.
- Click "Trigger DAG" to populate your dashboard with Shopify data.

---

## 📈 Using Your Dashboard

- View Shopify analytics updated automatically every 10 minutes.
- Interact with dynamic sales visualizations and forecasts.
- Easily filter by dates and products.

---

## 🛠 Troubleshooting

- **Docker issues?**  
  Confirm Docker Desktop is running; restart Docker if necessary.

- **Database connection errors?**  
  Ensure PostgreSQL credentials exactly match your `.env` file.

- **Empty dashboard or missing data?**  
  Verify Airflow DAG execution in Airflow UI and check logs for details.

Contact support at:  
`levesquenicolas95@gmail.com`

---

## 📄 License & Terms

Licensed under the terms outlined in the [LICENSE.md](LICENSE.md) file.

---

## 🎯 Next Steps

- **Deploy publicly with ease:** Recommended via Streamlit Cloud or Heroku.
- **Enhance your analytics:** Integrate inventory tracking, customer lifetime value, or marketing metrics.
- **Automate further:** Configure your DAG in Airflow to run daily at midnight automatically.

Enjoy powerful, hassle-free Shopify analytics!
