# 🛠️ Shopify Sales Dashboard - Setup Guide

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/NicolasLevesque/shopify-sales-dashboard.git
cd shopify-sales-dashboard
```

## 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

## 3️⃣ Set Up Shopify API Credentials

1. Go to **Shopify Partners** and create an API key.
2. Store credentials in `.env` file:

```ini
SHOP_NAME=your-shop-name
API_KEY=your-api-key
PASSWORD=your-api-password
```

## 4️⃣ Run Data Extraction Script

```bash
python scripts/extract_shopify_data.py
```

