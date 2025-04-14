import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
from prophet.make_holidays import make_holidays_df

load_dotenv()


def generate_forecast_plot():
    DB_CONFIG = {
        "host": os.getenv("POSTGRES_HOST"),
        "database": os.getenv("POSTGRES_DB"),
        "user": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
        "port": os.getenv("POSTGRES_PORT"),
    }

    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    query = """
    SELECT order_date::date as ds, 
           SUM(total_price::numeric) as y
    FROM synthetic_orders
    GROUP BY ds
    ORDER BY ds;
    """

    df_sales = pd.read_sql(query, engine)

    cap_value = df_sales["y"].max() * 1.5
    df_sales["cap"] = cap_value

    holidays = make_holidays_df(year_list=[2024, 2025], country="US")

    model_full = Prophet(
        growth="logistic",
        holidays=holidays,
        seasonality_mode="multiplicative",
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
    )

    model_full.fit(df_sales)

    future = model_full.make_future_dataframe(periods=14)
    future["cap"] = cap_value
    forecast = model_full.predict(future)

    fig = model_full.plot(forecast)
    plt.title("Sales Forecast")
    plt.xlabel("Date")
    plt.ylabel("Revenue ($)")

    return fig
