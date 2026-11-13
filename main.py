import json
import os
import sys
import time
from logger import setup_logger
from transform_silver import process_silver_hospedagens
from transform_gold import build_gold_layer
from ingest_notion import fetch_notion_database, DATABASE_ID
from mock_data import generate_mock_hospedagens

logger = setup_logger("MainPipeline")

def run_pipeline():
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("🐶 INICIANDO PIPELINE DOGHOUSE LAKEHOUSE (MEDALLION)")
    logger.info("=" * 60)

   # 1. Camada Bronze (Com suporte a Mock Data)
    logger.info("[1/3] 🥉 Processando Camada Bronze (Ingestão)...")

    raw_data = None
    notion_token = os.getenv("NOTION_TOKEN")

    if notion_token:
      logger.info(
          "🔑 Token do Notion detetado. A tentar extração via API real..."
      )
      raw_data = fetch_notion_database(DATABASE_ID)

    if not raw_data:
      logger.warning(
          "⚠️ Token ausente ou falha na API. A ativar modo HÍBRIDO (Dados"
          " Sintéticos/Mock)..."
      )
      mock_response = generate_mock_hospedagens()
      raw_data = mock_response.get("results", [])

    os.makedirs("data/bronze", exist_ok=True)
    bronze_path = "data/bronze/raw_hospedagens.json"
    with open(bronze_path, "w", encoding="utf-8") as f:
      json.dump(raw_data, f, ensure_ascii=False, indent=4)

    logger.info(
        f"✓ Bronze finalizada com sucesso: {len(raw_data)} registros salvos em"
        f" {bronze_path}"
    )

    # 2. Camada Silver
    logger.info("[2/3] 🥈 Processando Camada Silver (Tratamento & Pandera)...")
    process_silver_hospedagens()
    logger.info("✓ Silver finalizada com sucesso.")

    # 3. Camada Gold
    logger.info("[3/3] 🥇 Processando Camada Gold (Métricas & DuckDB)...")
    build_gold_layer()
    logger.info("✓ Gold finalizada com sucesso.")

    elapsed = round(time.time() - start_time, 2)
    logger.info("=" * 60)
    logger.info(f"✨ PIPELINE EXECUTADO COM SUCESSO EM {elapsed}s!")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_pipeline()