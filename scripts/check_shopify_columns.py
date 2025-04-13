import requests
from dotenv import load_dotenv
import os
import json

load_dotenv("../setup/.env")

SHOP_NAME = os.getenv("SHOP_NAME")
ADMIN_ACCESS_TOKEN = os.getenv("ADMIN_ACCESS_TOKEN")

url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2024-01/orders.json?limit=1"
headers = {
    "X-Shopify-Access-Token": ADMIN_ACCESS_TOKEN,
    "Content-Type": "application/json",
}

response = requests.get(url, headers=headers)
orders = response.json()

print(json.dumps(orders, indent=4))
