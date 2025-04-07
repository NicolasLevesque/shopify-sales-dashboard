import os
from dotenv import load_dotenv
import psycopg2
from hubspot import HubSpot
from hubspot.crm.contacts import PublicObjectSearchRequest, Filter, FilterGroup

# Load environment variables explicitly
load_dotenv()

# Connect explicitly to PostgreSQL
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

# Retrieve recent contacts explicitly from PostgreSQL
cursor.execute(
    """
    SELECT DISTINCT ON (email) first_name, last_name, email, phone, address
    FROM hubspot_contacts
    WHERE updated_at > NOW() - INTERVAL '1 day'
    ORDER BY email, updated_at DESC;
    """
)
contacts = cursor.fetchall()

# Validate contacts in HubSpot explicitly
for first_name, last_name, email, phone, address in contacts:
    search_request = PublicObjectSearchRequest(
        filter_groups=[
            FilterGroup(
                filters=[Filter(property_name="email", operator="EQ", value=email)]
            )
        ]
    )

    hubspot_contact = hubspot_client.crm.contacts.search_api.do_search(
        public_object_search_request=search_request
    )

    if hubspot_contact.total == 0:
        print(f"❌ Missing contact in HubSpot: {email}")
    else:
        properties = hubspot_contact.results[0].properties
        address_parts = [part.strip() for part in address.split(",")]

        mismatches = []
        if properties.get("firstname") != first_name:
            mismatches.append(
                f"firstname (DB: '{first_name}' | HubSpot: '{properties.get('firstname')}')"
            )
        if properties.get("lastname") != last_name:
            mismatches.append(
                f"lastname (DB: '{last_name}' | HubSpot: '{properties.get('lastname')}')"
            )
        if properties.get("phone") != phone:
            mismatches.append(
                f"phone (DB: '{phone}' | HubSpot: '{properties.get('phone')}')"
            )

        # Explicit address checks
        if properties.get("address") != (
            address_parts[0] if len(address_parts) > 0 else ""
        ):
            mismatches.append(
                f"address (DB: '{address_parts[0]}' | HubSpot: '{properties.get('address')}')"
            )
        if properties.get("city") != (
            address_parts[1] if len(address_parts) > 1 else ""
        ):
            mismatches.append(
                f"city (DB: '{address_parts[1]}' | HubSpot: '{properties.get('city')}')"
            )
        if properties.get("state") != (
            address_parts[2] if len(address_parts) > 2 else ""
        ):
            mismatches.append(
                f"state (DB: '{address_parts[2]}' | HubSpot: '{properties.get('state')}')"
            )
        if properties.get("zip") != (
            address_parts[-1].split(" ")[-1] if len(address_parts) >= 4 else ""
        ):
            mismatches.append(
                f"zip (DB: '{address_parts[-1].split(' ')[-1]}' | HubSpot: '{properties.get('zip')}')"
            )
        if properties.get("country") != "Canada":
            mismatches.append(
                f"country (DB: 'Canada' | HubSpot: '{properties.get('country')}')"
            )

        if mismatches:
            print(f"⚠️ Discrepancy for '{email}': {', '.join(mismatches)}")
        else:
            print(f"✅ Validated contact '{email}' successfully.")

# Explicitly close DB connection
cursor.close()
conn.close()

print("🎉 HubSpot contacts validation complete.")
