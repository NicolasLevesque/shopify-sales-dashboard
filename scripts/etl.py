import os
import json
import requests
import psycopg2
from datetime import datetime

# 1. Import load_dotenv
from dotenv import load_dotenv

# 2. Call load_dotenv() early in the file
load_dotenv()

def extract_shopify_orders():
    """ Extract orders from Shopify API using environment variables for credentials. """
    shop_name = os.getenv("SHOP_NAME")
    admin_access_token = os.getenv("ADMIN_ACCESS_TOKEN")
    
    url = f"https://{shop_name}.myshopify.com/admin/api/2023-10/orders.json?status=any"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": admin_access_token
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error if the status code is 4xx or 5xx
    data = response.json()
    return data.get("orders", [])

def transform_data(orders):
    """ Transform raw Shopify JSON into structured data for PostgreSQL. """
    customers_data = []
    orders_data = []
    products_data = []

    for order in orders:
        # 1. Customer
        customer_id = None
        customer_info = order.get("customer")
        if customer_info:
            shopify_customer_id = customer_info.get("id")
            email = customer_info.get("email", "")
            first_name = customer_info.get("first_name", "")
            last_name = customer_info.get("last_name", "")
            created_at = customer_info.get("created_at")
            updated_at = customer_info.get("updated_at")
            
            customers_data.append((
                shopify_customer_id,
                email,
                first_name,
                last_name,
                created_at,
                updated_at
            ))
            customer_id = shopify_customer_id
        
        # 2. Order
        shopify_order_id = order.get("id")
        total_price = order.get("total_price", 0)
        currency = order.get("currency", "")
        created_at = order.get("created_at")
        updated_at = order.get("updated_at")

        # Assign the Shopify customer ID to 'customer_id'
        customer_id = shopify_customer_id
        
        orders_data.append((
            shopify_order_id,
            customer_id,
            total_price,
            currency,
            created_at,
            updated_at
        ))

        # 3. Products
        line_items = order.get("line_items", [])
        for item in line_items:
            shopify_product_id = item.get("product_id")
            title = item.get("title")
            price = item.get("price")

            products_data.append((
                shopify_product_id,
                title,
                price,
                datetime.now(),  # or None
                datetime.now()
            ))
    
    return customers_data, orders_data, products_data

def load_data(customers, orders, products):
    """ Load the transformed data into PostgreSQL, using environment variables for DB credentials. """
    try:
        db_name = os.getenv("POSTGRES_DB", "shopify_data")
        db_user = os.getenv("POSTGRES_USER", "postgres")
        db_password = os.getenv("POSTGRES_PASSWORD", "airflow")
        db_host = os.getenv("POSTGRES_HOST", "postgres")
        db_port = os.getenv("POSTGRES_PORT", "5432")

        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        # 1. Insert Customers
        insert_customer_sql = """
        INSERT INTO customers (shopify_customer_id, email, first_name, last_name, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (shopify_customer_id) DO NOTHING;
        """
        for cust in customers:
            cursor.execute(insert_customer_sql, cust)
        
        # 2. Insert Orders
        insert_orders_sql = """
        INSERT INTO orders (shopify_order_id, customer_id, total_price, currency, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (shopify_order_id) DO NOTHING;
        """
        for ord_ in orders:
            cursor.execute(insert_orders_sql, ord_)
        
        # 3. Insert Products
        insert_products_sql = """
        INSERT INTO products (shopify_product_id, title, price, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (shopify_product_id) DO NOTHING;
        """
        for prod in products:
            cursor.execute(insert_products_sql, prod)
        
        conn.commit()
        
        print("✅ ETL Load Complete: Data inserted into customers, orders, and products.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error loading data: {e}")

def main():
    # 1. Extract
    orders = extract_shopify_orders()

    # # Uncomment this for testing failure alerts:
    # raise Exception("Testing email alert on failure")

    # 2. Transform
    customers_data, orders_data, products_data = transform_data(orders)
    
    # 3. Load
    load_data(customers_data, orders_data, products_data)

if __name__ == "__main__":
    main()
