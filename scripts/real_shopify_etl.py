from dotenv import load_dotenv
import os
import shopify
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

# Shopify credentials from .env
SHOP_NAME = os.getenv("SHOP_NAME")
ADMIN_ACCESS_TOKEN = os.getenv("ADMIN_ACCESS_TOKEN")

# Database credentials from .env
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "port": int(os.getenv("POSTGRES_PORT")),
}


def fetch_real_shopify_orders():
    api_version = "2024-01"
    session = shopify.Session(
        f"{SHOP_NAME}.myshopify.com", api_version, ADMIN_ACCESS_TOKEN
    )
    shopify.ShopifyResource.activate_session(session)

    orders = shopify.Order.find(status="any", limit=250)

    orders_data = []
    for order in orders:
        for item in order.line_items:
            orders_data.append(
                {
                    "order_id": order.id,
                    "order_date": order.created_at,
                    "product": item.name,
                    "customer_first_name": (
                        order.customer.first_name if order.customer else None
                    ),
                    "customer_last_name": (
                        order.customer.last_name if order.customer else None
                    ),
                    "customer_email": order.email,
                    "financial_status": order.financial_status,
                    "fulfillment_status": order.fulfillment_status,
                    "currency": order.currency,
                    "subtotal_price": order.subtotal_price,
                    "total_price": order.total_price,
                    "total_tax": order.total_tax,
                    "total_discounts": order.total_discounts,
                    "total_shipping": (
                        order.total_shipping_price_set.presentment_money.amount
                        if order.total_shipping_price_set
                        else 0
                    ),
                    "gateway": getattr(order, "gateway", None),
                    "created_at": order.created_at,
                    "updated_at": order.updated_at,
                }
            )

    shopify.ShopifyResource.clear_session()

    return orders_data


def load_orders_to_postgres(orders_data):
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    df = pd.DataFrame(orders_data)
    df.to_sql("real_orders", engine, if_exists="replace", index=False)
    print("✅ Real Shopify orders loaded into PostgreSQL successfully.")


if __name__ == "__main__":
    orders = fetch_real_shopify_orders()
    load_orders_to_postgres(orders)
