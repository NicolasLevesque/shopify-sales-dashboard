import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

load_dotenv()

# Load environment variables
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": os.getenv("POSTGRES_PORT"),
}

# Establish connection
engine = create_engine(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Query historical sales data
query = """
SELECT order_date::date as ds, 
       SUM(total_price::numeric) as y
FROM synthetic_orders
GROUP BY ds
ORDER BY ds;
"""

df_sales = pd.read_sql(query, engine)

# Prophet model for forecasting
model = Prophet()
model.fit(df_sales)

# Create future dataframe (forecast next 14 days)
future = model.make_future_dataframe(periods=14)

# Forecast future sales
forecast = model.predict(future)

# Plot forecast
fig = model.plot(forecast)
plt.title("Sales Forecast")
plt.xlabel("Date")
plt.ylabel("Revenue ($)")
plt.savefig("/opt/airflow/images/sales_forecast_plot.png")

print("✅ Sales forecast created successfully.")
