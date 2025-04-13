from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv("../setup/.env")

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

CREATE_REAL_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS real_orders (
    order_id BIGINT PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    customer_name TEXT,
    customer_email TEXT,
    product TEXT,
    quantity INTEGER,
    price NUMERIC(10,2),
    total_price NUMERIC(10,2),
    discount_code TEXT,
    financial_status TEXT,
    fulfillment_status TEXT,
    currency TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

with engine.connect() as conn:
    conn.execute(text(CREATE_REAL_ORDERS_TABLE))
    conn.commit()

print("✅ Real orders table created successfully.")
