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


def getName(result) -> str:
    return result["properties"]["Name"]["title"][0]["plain_text"]


def getFile(result):
    return result["properties"]["Receipt File"]["files"][0]


def getPurchaseDate(result):
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
    oldName = getFile(result)["name"]
    newName = getPurchaseDate(result) + "_" + getName(result).replace(" ", "") + ".pdf"
    if oldName != newName:
        print("Old Name: " + oldName + " | New Name: " + newName)
        properties = {"Receipt File": result["properties"]["Receipt File"]}
        properties["Receipt File"]["files"][0]["name"] = newName
        update_properties(page_id, properties)
    else:
        print("Name unchanged: " + oldName)