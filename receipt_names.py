import re
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DB_ID")

local_env = True
if os.getenv("GITHUB_ACTIONS") == "true":
    local_env = False

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
    if local_env:
        with open("response.json", "w") as file:
            json.dump(data, file, indent=2)

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

    if local_env:
        with open("response2.json", "w") as file:
            json.dump(data, file, indent=2)

    return data


def update_icon(page_id, icon):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"icon": icon}
    response = requests.patch(url, json=payload, headers=headers)
    data = response.json()

    if local_env:
        with open("response3.json", "w") as file:
            json.dump(data, file, indent=2)

    return data


def clean_and_capitalize(string):
    cleaned_string = re.sub(r"[^a-zA-Z0-9 ]", "", string)
    capitalized_string = " ".join(
        word[0].upper() + word[1:] for word in cleaned_string.split()
    )
    return capitalized_string


results = []

for result in get_pages():
    if len(result["properties"]["Receipt File"]["files"]) != 1:
        continue

    page_id = result["id"]

    old_page_name = get_name(result)
    new_page_name = clean_and_capitalize(old_page_name)

    old_file_name = get_file(result)["name"]
    new_file_name = (
        get_purchase_date(result) + "_" + new_page_name.replace(" ", "") + ".pdf"
    )

    if old_file_name != new_file_name or old_page_name != new_page_name:
        print("[[PAGE]] Old Name: " + old_page_name + " | New Name: " + new_page_name)
        print("[[FILE]] Old Name: " + old_file_name + " | New Name: " + new_file_name)

        properties = {
            "Receipt File": result["properties"]["Receipt File"],
            "Name": result["properties"]["Name"],
        }
        properties["Receipt File"]["files"][0]["name"] = new_file_name
        properties["Name"]["title"][0]["plain_text"] = new_page_name

        update_properties(page_id, properties)
    else:
        print("Name unchanged: " + old_file_name)

    if not result["icon"]:
        print("No icon for " + new_page_name + ", updating...")
        receipt_icon = {
            "type": "external",
            "external": {"url": "https://www.notion.so/icons/receipt_gray.svg"},
        }
        update_icon(page_id, receipt_icon)
