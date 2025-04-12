import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet.make_holidays import make_holidays_df

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

# Split into training and validation sets (last 14 days for validation)
train = df_sales.iloc[:-14]
valid = df_sales.iloc[-14:]

# Include holidays (adjust country as needed)
holidays = make_holidays_df(year_list=[2024, 2025], country="US")

# Prophet model with enhanced settings
model = Prophet(
    holidays=holidays,
    seasonality_mode="multiplicative",
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
)

# Train model on training data
model.fit(train)

# Validate predictions
forecast_valid = model.predict(valid[["ds"]])
valid = valid.copy()
valid["predicted"] = forecast_valid["yhat"].values

# Calculate accuracy metrics
mae = mean_absolute_error(valid["y"], valid["predicted"])
rmse = mean_squared_error(valid["y"], valid["predicted"])
rmse = rmse**0.5  # Clearly calculate RMSE


print(f"Validation MAE: {mae:.2f}")
print(f"Validation RMSE: {rmse:.2f}")

# Add a 'cap' to limit growth (set to 1.5x max historical sales)
cap_value = df_sales["y"].max() * 1.5
df_sales["cap"] = cap_value


# Create a new Prophet instance for retraining on entire dataset
model_full = Prophet(
    growth="logistic",
    holidays=holidays,
    seasonality_mode="multiplicative",
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
)

# Retrain model on entire dataset before forecasting future
model_full.fit(df_sales)

# Create future dataframe (forecast next 14 days)
future = model_full.make_future_dataframe(periods=14)
future["cap"] = cap_value
forecast = model_full.predict(future)

# Plot forecast
fig = model_full.plot(forecast)
plt.title("Sales Forecast")
plt.xlabel("Date")
plt.ylabel("Revenue ($)")
plt.savefig("/opt/airflow/images/sales_forecast_plot.png")

print("✅ Sales forecast created successfully.")
