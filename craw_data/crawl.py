import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random
import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bs4 import BeautifulSoup
from html import unescape

def clean_html(html_text):
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return unescape(soup.get_text(separator=" ", strip=True))
# Load .env for MongoDB access


# Connect to MongoDB
client = MongoClient('mongodb+srv://khoibk123123:khoibk123@recommenddtb.4in6a.mongodb.net/?retryWrites=true&w=majority&appName=RecommendDTB', server_api=ServerApi('1'))
db = client['Steam_Game']
collection = db['Steam_data']


# Confirm connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    exit(1)

# Insert single document

def insert_into_mongodb(data):
    try:
        collection.insert_one(data)
        print(f"✅ Inserted: {data['app_id']} - {data['name']}")
    except DuplicateKeyError:
        print(f"⏭ Duplicate skipped: {data['app_id']}")
    except pymongo.errors.PyMongoError as e:
        print(f"❌ MongoDB Error: {e}")

# Load app IDs
with open("cleaned_steam_apps.json", "r", encoding="utf-8") as f:
    app_data = json.load(f)
all_app_ids = [app["appid"] for app in app_data["applist"]["apps"]]
start_from = 3151000
all_app_ids = [appid for appid in all_app_ids if appid >= start_from]

existing_ids = set(collection.distinct("app_id"))
app_ids = [appid for appid in all_app_ids if appid not in existing_ids]
print(f"⏭ Skipping {len(existing_ids)} already in MongoDB. Remaining: {len(app_ids)}")

# Set up HTTP session with retries
session = requests.Session()
retry_strategy = Retry(
    total=2,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    respect_retry_after_header=True,
)
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5"
}


def extract_sys_req_fields(html_text):
    """Extract system requirement fields from HTML text"""
    fields = {
        "os": "",
        "processor": "",
        "memory": "",
        "graphics": "",
        "directx": "",
        "network": "",
        "storage": ""
    }
    if not html_text:
        return fields

    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.find_all("li")
    for item in items:
        text = item.get_text(strip=True)
        if "OS" in text:
            fields["os"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "Processor" in text:
            fields["processor"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "Memory" in text:
            fields["memory"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "Graphics" in text:
            fields["graphics"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "DirectX" in text:
            fields["directx"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "Network" in text:
            fields["network"] = text.split(":", 1)[-1].strip() if ":" in text else text
        elif "Storage" in text:
            fields["storage"] = text.split(":", 1)[-1].strip() if ":" in text else text

    return fields


def fetch_app_details(app_id):
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=us&l=en"
        response = session.get(url, headers=headers, timeout=15)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"Rate limited: waiting {retry_after}s for app {app_id}...")
            time.sleep(retry_after)
            return None
        response.raise_for_status()
        data = response.json()
        if str(app_id) in data and data[str(app_id)]["success"]:
            return data[str(app_id)]["data"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error on {app_id}: {e}")
        return None
    except Exception as e:
        print(f"Unknown error on {app_id}: {e}")
        return None

def process_app_data(app_id):
    try:
        print(f" Processing: {app_id}")
        time.sleep(random.uniform(2, 4))
        app_data = fetch_app_details(app_id)
        if not app_data:
            print(f" Failed: {app_id}")
            return

        pc_min = extract_sys_req_fields(app_data.get("pc_requirements", {}).get("minimum", ""))
        pc_rec = extract_sys_req_fields(app_data.get("pc_requirements", {}).get("recommended", ""))

        price = app_data.get("price_overview", {})
        price_currency = price.get("currency", "")
        price_final = price.get("final_formatted", "Free" if app_data.get("is_free") else "")
        discount = price.get("discount_percent", 0)

        result = {
            "app_id": app_id,
            "name": app_data["name"],
            "type": app_data.get("type", ""),
            "required_age": app_data.get("required_age", ""),
            "is_free": app_data.get("is_free", False),
            "short_description": clean_html(app_data.get("short_description", "")),
            "detailed_description": clean_html(app_data.get("detailed_description", "")[:1000]),
            "about_the_game": clean_html(app_data.get("about_the_game", "")[:1000]),
            "supported_languages": clean_html(app_data.get("supported_languages", "")),
            "website": app_data.get("website", ""),
            "developers": ", ".join(app_data.get("developers", [])),
            "publishers": ", ".join(app_data.get("publishers", [])),
            "price_currency": price_currency,
            "price_final": price_final,
            "discount_percent": discount,
            "platforms_windows": app_data.get("platforms", {}).get("windows", False),
            "platforms_mac": app_data.get("platforms", {}).get("mac", False),
            "platforms_linux": app_data.get("platforms", {}).get("linux", False),
            "metacritic_score": app_data.get("metacritic", {}).get("score", ""),
            "categories": ", ".join([cat["description"] for cat in app_data.get("categories", [])]),
            "genres": ", ".join([genre["description"] for genre in app_data.get("genres", [])]),
            "recommendations_total": app_data.get("recommendations", {}).get("total", 0),
            "release_date": app_data.get("release_date", {}).get("date", ""),
            "support_email": app_data.get("support_info", {}).get("email", ""),
            "pc_min_os": pc_min["os"], "pc_min_processor": pc_min["processor"], "pc_min_memory": pc_min["memory"],
            "pc_min_graphics": pc_min["graphics"], "pc_min_directx": pc_min["directx"],
            "pc_min_network": pc_min["network"], "pc_min_storage": pc_min["storage"],
            "pc_rec_os": pc_rec["os"], "pc_rec_processor": pc_rec["processor"], "pc_rec_memory": pc_rec["memory"],
            "pc_rec_graphics": pc_rec["graphics"], "pc_rec_directx": pc_rec["directx"],
            "pc_rec_network": pc_rec["network"], "pc_rec_storage": pc_rec["storage"],
            "header_image": app_data.get("header_image", ""),
            "background": app_data.get("background", ""),
            "screenshots_count": len(app_data.get("screenshots", [])),
            "movies_count": len(app_data.get("movies", []))
        }

        insert_into_mongodb(result)
    except Exception as e:
        print(f"Error processing app ID {app_id}: {e}")

# Main executor
if __name__ == "__main__":
    max_workers = 5
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_app_data, app_id) for app_id in app_ids]
        for future in as_completed(futures):
            pass
