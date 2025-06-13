import os
import requests
from notion_client import Client

# 從環境變數讀取金鑰
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

notion = Client(auth=NOTION_TOKEN)

def get_places():
    response = notion.databases.query(database_id=DATABASE_ID)
    return response["results"]

def update_place_url(page_id, url):
    notion.pages.update(
        page_id=page_id,
        properties={
            "Google Maps 連結": {
                "url": url
            }
        }
    )

def get_google_maps_url(place_name):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": place_name, "key": GOOGLE_API_KEY}
    response = requests.get(endpoint, params=params).json()
    if response["status"] == "OK":
        latlng = response["results"][0]["geometry"]["location"]
        return f"https://www.google.com/maps/search/?api=1&query={latlng['lat']},{latlng['lng']}"
    else:
        return None

for page in get_places():
    props = page["properties"]
    name = props.get("地點", {}).get("title", [{}])[0].get("text", {}).get("content", "")
    if not name:
        continue
    url = get_google_maps_url(name)
    if url:
        update_place_url(page["id"], url)
