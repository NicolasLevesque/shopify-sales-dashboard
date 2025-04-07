import os
from dotenv import load_dotenv
import psycopg2
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInput as ContactInput
from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup
from hubspot.crm.contacts.exceptions import ApiException

load_dotenv()

# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
)
cursor = conn.cursor()

# HubSpot client initialization
hubspot_client = HubSpot(access_token=os.getenv("HUBSPOT_API_KEY"))

# Fetch explicitly updated contacts
cursor.execute(
    """
    SELECT DISTINCT ON (email) first_name, last_name, email, phone, address
    FROM hubspot_contacts
    ORDER BY email, updated_at DESC;
    """
)
contacts = cursor.fetchall()

# Sync explicitly contacts only
for first_name, last_name, email, phone, address in contacts:
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

    search_request = PublicObjectSearchRequest(
        filter_groups=[
            FilterGroup(
                filters=[Filter(property_name="email", operator="EQ", value=email)]
            )
        ]
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

cursor.close()
conn.close()

print("🎉 Contacts explicitly synced to HubSpot.")
