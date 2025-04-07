import os
from dotenv import load_dotenv
import psycopg2
from hubspot import HubSpot
from hubspot.crm.deals import SimplePublicObjectInput as DealInput
from hubspot.crm.deals.exceptions import ApiException

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
)
cursor = conn.cursor()

hubspot_client = HubSpot(access_token=os.getenv("HUBSPOT_API_KEY"))

cursor.execute(
    """
    SELECT order_id, associated_contact_email, deal_create_date, amount, deal_stage, payment_method
    FROM hubspot_deals
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
