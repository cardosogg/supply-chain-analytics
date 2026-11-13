import json
import os
import pandas as pd
import pandera.pandas as pa
from logger import setup_logger

logger = setup_logger("TransformSilver")

# Definição do Contrato de Dados com Pandera (versão moderna)
silver_schema = pa.DataFrameSchema({
    "page_id": pa.Column(str),
    "nome_cao": pa.Column(str, nullable=False),
    "data_entrada": pa.Column(str, nullable=False),
    "forma_pagamento": pa.Column(str, nullable=True),
    "valor_total": pa.Column(float, nullable=True, required=False),
})


def process_silver_hospedagens():
  logger.info("Lendo dados brutos da Camada Bronze...")
  bronze_path = "data/bronze/raw_hospedagens.json"

  if not os.path.exists(bronze_path):
    logger.error(f"Ficheiro bronze não encontrado em {bronze_path}")
    return

  with open(bronze_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

  # Tratar caso o JSON seja uma lista simples ou dicionário com "results"
  records = raw_data if isinstance(raw_data, list) else raw_data.get("results", [])

  processed_rows = []
  for item in records:
    # Se os dados vierem do mock ou do Notion em formato de propriedades
    if "properties" in item:
      props = item["properties"]
      page_id = item.get("id", "unknown")

      # Extração segura de campos do Notion
      # Nota: Ajustando para ler o nome do cão do campo correto (Hóspede ou Nome)
      hospede_field = props.get("Hóspede", props.get("Nome", {}))
      nome_cao = "Desconhecido"
      if "title" in hospede_field and hospede_field["title"]:
        nome_cao = hospede_field["title"][0]["text"]["content"]
      elif "rich_text" in hospede_field and hospede_field["rich_text"]:
        nome_cao = hospede_field["rich_text"][0]["text"]["content"]

      # Data de Entrada
      data_entrada = None
      date_prop = props.get("Entrada", props.get("Data Entrada", {}))
      if "date" in date_prop and date_prop["date"]:
        data_entrada = date_prop["date"].get("start")

      # Forma de Pagamento
      pagamento_prop = props.get("Forma de pagamento", props.get("Forma de Pagamento", {}))
      forma_pagamento = "Não Informado"
      if "select" in pagamento_prop and pagamento_prop["select"]:
        forma_pagamento = pagamento_prop["select"].get("name", "Não Informado")

      # Valor Total / Diárias
      valor_total = 0.0
      val_prop = props.get("Valor final", props.get("Valor Total", {}))
      if "number" in val_prop:
        valor_total = val_prop["number"] or 0.0

      processed_rows.append({
          "page_id": page_id,
          "nome_cao": nome_cao,
          "data_entrada": data_entrada,
          "forma_pagamento": forma_pagamento,
          "valor_total": float(valor_total),
      })
    else:
      # Caso já venha pré-formatado pelo mock antigo
      processed_rows.append(item)

  df = pd.DataFrame(processed_rows)

  # Tratamento de nulos e limpeza básica
  df["forma_pagamento"] = df["forma_pagamento"].fillna("Não Informado")
  df["nome_cao"] = df["nome_cao"].fillna("Desconhecido")

  logger.info("🧪 Validando estrutura dos dados com Pandera...")
  try:
    validated_df = silver_schema.validate(df, lazy=True)
    logger.info("✓ Validadores do Pandera aprovados com sucesso!")
  except Exception as e:
    logger.error(f"❌ Erro de validação no contrato Pandera: {e}")
    raise e

  os.makedirs("data/silver", exist_ok=True)
  silver_path = "data/silver/hospedagens_limpo.parquet"
  validated_df.to_parquet(silver_path, index=False)
  logger.info(f"✓ Sucesso! Dados limpos salvos em: {silver_path}")


if __name__ == "__main__":
  process_silver_hospedagens()