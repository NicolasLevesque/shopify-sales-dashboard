import os
from dotenv import load_dotenv
import psycopg2
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput as ContactInput
from hubspot.crm.deals import SimplePublicObjectInput as DealInput
from hubspot.crm.line_items import SimplePublicObjectInput as LineItemInput
from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup
from hubspot.crm.line_items import PublicObjectSearchRequest as ProductSearchRequest
from hubspot.crm.deals import PublicObjectSearchRequest as DealSearchRequest
from hubspot.crm.contacts.exceptions import ApiException

# Explicitly load environment variables
load_dotenv()

# PostgreSQL connection explicitly defined
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
)
cursor = conn.cursor()

# Initialize HubSpot client explicitly
hubspot_client = HubSpot(access_token=os.getenv("HUBSPOT_API_KEY"))

# ----------------------------
# Explicitly sync contacts
# ----------------------------
# For contacts:
cursor.execute(
    """
SELECT DISTINCT ON (email) first_name, last_name, email, phone, address
FROM hubspot_contacts
WHERE updated_at > NOW() - INTERVAL '1 day'
ORDER BY email, updated_at DESC;
"""
)
contacts = cursor.fetchall()

for first_name, last_name, email, phone, address in contacts:
    search_request = PublicObjectSearchRequest(
        filter_groups=[
            FilterGroup(
                filters=[Filter(property_name="email", operator="EQ", value=email)]
            )
        ]
    )

    address_parts = [part.strip() for part in address.split(",")]

    contact_data = ContactInput(
        properties={
            "email": email,
            "firstname": first_name,
            "lastname": last_name,
            "phone": phone,
            "address": address_parts[0] if len(address_parts) > 0 else "",
            "city": address_parts[1] if len(address_parts) > 1 else "",
            "state": address_parts[2] if len(address_parts) > 2 else "",
            "zip": address_parts[-1].split(" ")[-1] if len(address_parts) >= 4 else "",
            "country": "Canada",
        }
    )

    try:
        existing_contact = hubspot_client.crm.contacts.search_api.do_search(
            public_object_search_request=search_request
        )

        if existing_contact.total == 0:
            hubspot_client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=contact_data
            )
            print(f"✅ Contact '{email}' added.")
        else:
            contact_id = existing_contact.results[0].id
            hubspot_client.crm.contacts.basic_api.update(
                contact_id=contact_id, simple_public_object_input=contact_data
            )
            print(f"🔄 Contact '{email}' updated.")
    except ApiException as e:
        print(f"⚠️ Error processing contact '{email}': {e}")

# ----------------------------
# Explicitly sync products (line items)
# ----------------------------
cursor.execute(
    """
SELECT DISTINCT ON (sku) product_name, sku, price
FROM hubspot_products
WHERE updated_at > NOW() - INTERVAL '1 day'
ORDER BY sku, updated_at DESC;
"""
)
products = cursor.fetchall()

for product_name, sku, price in products:
    search_request = ProductSearchRequest(
        filter_groups=[
            FilterGroup(
                filters=[Filter(property_name="hs_sku", operator="EQ", value=sku)]
            )
        ]
    )

    product_data = LineItemInput(
        properties={
            "name": product_name,
            "hs_sku": sku,
            "price": str(price),
        }
    )

    try:
        existing_product = hubspot_client.crm.line_items.search_api.do_search(
            public_object_search_request=search_request
        )

        if existing_product.total == 0:
            hubspot_client.crm.line_items.basic_api.create(
                simple_public_object_input_for_create=product_data
            )
            print(f"✅ Product '{product_name}' added.")
        else:
            product_id = existing_product.results[0].id
            hubspot_client.crm.line_items.basic_api.update(
                line_item_id=product_id, simple_public_object_input=product_data
            )
            print(f"🔄 Product '{product_name}' updated.")
    except Exception as e:
        print(f"⚠️ Error processing product '{product_name}': {e}")

# ----------------------------
# Explicitly sync deals
# ----------------------------
cursor.execute(
    """
    SELECT order_id, associated_contact_email, deal_create_date, amount, deal_stage, payment_method
    FROM hubspot_deals
    WHERE updated_at > NOW() - INTERVAL '1 day';
"""
)

deals = cursor.fetchall()

# Deal stage mapping

valid_stages = {
    "appointmentscheduled",
    "qualifiedtobuy",
    "presentationscheduled",
    "decisionmakerboughtin",
    "contractsent",
    "closedwon",
    "closedlost",
    "processing",
    "cancelled",
    "completed",
    "shipped",
}

deal_stage_mapping = {
    "processing": "1325803477",
    "cancelled": "1325803478",
    "completed": "1325803479",
    "shipped": "1325803482",
    "closedwon": "closedwon",
    "closedlost": "closedlost",
}

for order_id, email, deal_date, amount, stage, payment_method in deals:
    if stage not in valid_stages:
        print(f"Skipping deal '{order_id}': Invalid stage '{stage}'")
        continue

    hubspot_stage_id = deal_stage_mapping.get(stage, "appointmentscheduled")

    deal_data = DealInput(
        properties={
            "dealname": f"Order #{order_id}",
            "amount": str(amount),
            "dealstage": hubspot_stage_id,
            "closedate": deal_date.isoformat(),
            "payment_method": payment_method,
        }
    )

    try:
        hubspot_client.crm.deals.basic_api.create(
            simple_public_object_input_for_create=deal_data
        )
        print(f"✅ Deal '{order_id}' added.")
    except ApiException as e:
        print(f"⚠️ Error processing deal '{order_id}': {e}")

cursor.close()
conn.close()

# Clean up
cursor.close()
conn.close()
print("🎉 All data synced to HubSpot.")
