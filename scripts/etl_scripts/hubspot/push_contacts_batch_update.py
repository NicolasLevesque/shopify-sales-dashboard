import os
from dotenv import load_dotenv
import psycopg2
from hubspot import HubSpot
from hubspot.crm.contacts import BatchInputSimplePublicObjectBatchInput as BatchInput
from hubspot.crm.contacts import SimplePublicObjectBatchInput as ContactInput
from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup

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
    SELECT DISTINCT ON (email) first_name, last_name, email, phone, address
    FROM hubspot_contacts
    ORDER BY email, updated_at DESC;
"""
)
contacts = cursor.fetchall()

batch_size = 100

for i in range(0, len(contacts), batch_size):
    batch_contacts = contacts[i : i + batch_size]
    batch_updates = []

    for first_name, last_name, email, phone, address in batch_contacts:
        search_request = PublicObjectSearchRequest(
            filter_groups=[
                FilterGroup(
                    filters=[Filter(property_name="email", operator="EQ", value=email)]
                )
            ]
        )

        existing_contact = hubspot_client.crm.contacts.search_api.do_search(
            public_object_search_request=search_request
        )

        if existing_contact.total > 0:
            contact_id = existing_contact.results[0].id

            contact_data = ContactInput(
                id=contact_id,
                properties={
                    "email": email,
                    "firstname": first_name,
                    "lastname": last_name,
                    "phone": phone,
                    "address": address.split(",")[0].strip(),
                    "city": address.split(",")[1].strip(),
                    "state": address.split(",")[2].strip(),
                    "country": "Canada",
                    "zip": address.split(",")[-1].strip(),
                },
            )

            batch_updates.append(contact_data)
        else:
            print(f"❌ No contact found for '{email}'.")

    if batch_updates:
        batch_request = BatchInput(inputs=batch_updates)

        try:
            hubspot_client.crm.contacts.batch_api.update(batch_request)
            print(f"✅ Batch {i//batch_size + 1} contacts explicitly updated.")
        except Exception as e:
            print(f"⚠️ Error updating batch {i//batch_size + 1}: {e}")

cursor.close()
conn.close()

print("🎉 All contacts explicitly batch-updated to HubSpot.")
