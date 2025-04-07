# HubSpot ETL SQL Scripts

This folder contains SQL scripts explicitly designed to transform synthetic Shopify data into formatted tables ready for HubSpot integration.

## Execution Order

1. `01_create_contacts.sql` – Creates unique customer contact records.
2. `02_create_deals.sql` – Creates deals (orders) linked explicitly to contacts.
3. `03_create_products.sql` – Generates a unique product catalog.

Run each script in the listed order to ensure data integrity and proper dependencies.

## Usage

Execute scripts directly using PostgreSQL clients (pgAdmin, psql, etc.):

```bash
psql -h your_host -U your_user -d your_db -f 01_create_contacts.sql
psql -h your_host -U your_user -d your_db -f 02_create_deals.sql
psql -h your_host -U your_user -d your_db -f 03_create_products.sql
```

---

## HubSpot Integration Process

### SQL Scripts:

- **01_create_contacts.sql**: Extracts unique contacts from `synthetic_orders`, includes mandatory email validation.
- **02_create_deals.sql**: Extracts deal data matching HubSpot schema, ensuring timestamp accuracy.
- **03_create_products.sql**: Extracts product data with `updated_at` tracking for freshness.

### Python Integration Scripts:

- **push_data_to_hubspot.py**:
  - Utilizes HubSpot API (v3 CRM objects endpoint).
  - Pushes transformed data into HubSpot.
  - Supports batch operations and comprehensive error logging.

### API Call Example:

```http
POST https://api.hubapi.com/crm/v3/objects/contacts
Authorization: Bearer {API_KEY}
Content-Type: application/json

{
    "properties": {
        "email": "example@example.com",
        "firstname": "John",
        "lastname": "Doe",
        "phone": "555-555-5555"
    }
}
```

---

### Validation

Run the provided validation script (`validate_hubspot_sync.py`) after data integration:

- Confirms accurate record counts.
- Validates consistency between PostgreSQL source data and HubSpot data.

Document validation results clearly for auditing purposes.
