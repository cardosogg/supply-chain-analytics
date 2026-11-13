import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")

# ID oficial da database de Controle de Hospedagens
DATABASE_ID = "3eaef843-1e7d-809c-bb68-f9748496f43c"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def fetch_notion_database(database_id):
  url = f"https://api.notion.com/v1/databases/{database_id}/query"
  payload = {"page_size": 100}
  results = []
  has_more = True
  next_cursor = None

  print("Iniciando extração dos dados de Hospedagem (Camada Bronze)...")

  while has_more:
    if next_cursor:
      payload["start_cursor"] = next_cursor

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
      print(f"Erro na requisição: {response.status_code}")
      print(response.text)
      break

    data = response.json()
    results.extend(data.get("results", []))

    has_more = data.get("has_more", False)
    next_cursor = data.get("next_cursor", None)

  return results


if __name__ == "__main__":
  raw_data = fetch_notion_database(DATABASE_ID)

  if raw_data:
    os.makedirs("data/bronze", exist_ok=True)
    output_path = "data/bronze/raw_hospedagens.json"

    with open(output_path, "w", encoding="utf-8") as f:
      json.dump(raw_data, f, ensure_ascii=False, indent=4)

    print(
        f" Sucesso! {len(raw_data)} registros extraídos e salvos em:"
        f" {output_path}"
    )