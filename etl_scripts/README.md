# HubSpot ETL SQL Scripts

This folder contains SQL scripts explicitly designed to transform synthetic Shopify data into clearly formatted tables ready for HubSpot integration.

## Execution Order

1. `01_create_contacts.sql` – creates unique customer contact records.
2. `02_create_deals.sql` – creates deals (orders) linked to contacts.
3. `03_create_products.sql` – generates a unique product catalog.

Run each script in the listed order explicitly to ensure data integrity and proper dependencies.

## Usage

Execute scripts directly in PostgreSQL (pgAdmin, psql, or other PostgreSQL client):

```bash
psql -h postgres -U your_user -d your_db -f 01_create_contacts.sql
psql -h your_host -U your_user -d your_db -f 02_create_deals.sql
psql -h your_host -U your_user -d your_db -f 03_create_products.sql
```

---
