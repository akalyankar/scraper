import requests 
from openpyxl import Workbook
from dotenv import load_dotenv
import os 
import time

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
LOCATION = os.getenv("LOCATION")
SEARCH_TERM = os.getenv("SEARCH_TERM")
RADIUS = os.getenv("RADIUS")


search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"


params = {
    "query": f"{SEARCH_TERM} in {LOCATION}",
    "radius": RADIUS,
    "key": API_KEY
}

results = []

print("Searching for dealerships...")

while True:
    resp = requests.get(search_url, params=params)
    data = resp.json()
    results.extend(data.get("results", []))

    next_page = data.get("next_page_token")
    if not next_page:
        break


    time.sleep(2)
    params = {"pagetoken": next_page, "key": API_KEY}

wb = Workbook()
ws = wb.active
ws.title = "Dealerships"
ws.append(["Name", "Phone", "Address", "Opening Hours"])

print(f"Found {len(results)} dealerships. Fetching details...")

for place in results:
    place_id = place.get("place_id")
    name = place.get("name", "")
    address = place.get("formatted_address", "")

    details_params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,opening_hours",
        "key": API_KEY
    }

    detail_resp = requests.get(details_url, params=details_params)
    detail_data = detail_resp.json().get("result", {})

    phone = detail_data.get("formatted_phone_number", "N/A")
    hours = detail_data.get("opening_hours", {}).get("weekday_text", [])
    hours_str = "\n".join(hours) if hours else "N/A"

    ws.append([name, phone, address, hours_str])


wb.save("google_dealerships.xlsx")
print("Saved to google_dealerships.xlsx")