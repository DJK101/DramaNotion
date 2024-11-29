import requests
from dotenv import load_dotenv
import os

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DB_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_pages():
    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"

    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    return data["results"]


def get_name(result) -> str:
    return result["properties"]["Name"]["title"][0]["plain_text"]


def get_file(result):
    return result["properties"]["Receipt File"]["files"][0]


def get_purchase_date(result):
    return result["properties"]["Receipt Date"]["date"]["start"]


def update_properties(page_id, properties):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"properties": properties}
    response = requests.patch(url, json=payload, headers=headers)
    data = response.json()

    return data


results = []

for result in get_pages():
    if len(result["properties"]["Receipt File"]["files"]) != 1:
        continue

    page_id = result["id"]

    old_file_name = get_file(result)["name"]
    new_file_name = get_purchase_date(result) + "_" + get_name(result).replace(" ", "") + ".pdf"
    if old_file_name != new_file_name:
        print("Old Name: " + old_file_name + " | New Name: " + new_file_name)
        properties = {"Receipt File": result["properties"]["Receipt File"]}
        properties["Receipt File"]["files"][0]["name"] = new_file_name
        update_properties(page_id, properties)
    else:
        print("Name unchanged: " + old_file_name)