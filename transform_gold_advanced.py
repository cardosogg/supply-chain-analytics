import os
import duckdb


def build_advanced_gold_metrics():
  silver_path = "data/silver/hospedagens_limpo.parquet"
  gold_dir = "data/gold"

  if not os.path.exists(silver_path):
    print(f"❌ Arquivo Silver não encontrado em {silver_path}.")
    return

  print("🚀 Processando Métricas Gold Avançadas com DuckDB...\n")
  con = duckdb.connect("data/gold/doghouse.duckdb")

  # 1. Visão de Faturamento e Ticket Médio
  df_financeiro = con.execute(f"""
        WITH parsed_dates AS (
            SELECT 
                "Hóspede",
                "Cão",
                "Forma de pagamento",
                CAST("Desconto" AS DOUBLE) AS desconto,
                CAST("Valor horas adicionais" AS DOUBLE) AS valor_horas_add,
                TRY_CAST("Entrada" AS TIMESTAMP) AS dt_entrada
            FROM read_parquet('{silver_path}')
        )
        SELECT 
            STRFTIME(dt_entrada, '%Y-%m') AS ano_mes,
            COUNT(*) AS total_hospedagens,
            ROUND(AVG(COALESCE(valor_horas_add, 0)), 2) AS ticket_medio_horas_add,
            ROUND(SUM(COALESCE(valor_horas_add, 0)), 2) AS receita_horas_add_total
        FROM parsed_dates
        WHERE dt_entrada IS NOT NULL
        GROUP BY 1
        ORDER BY ano_mes DESC;
    """).df()

  print("--- 💰 Métricas Financeiras Consolidadas por Mês ---")
  print(df_financeiro)
  print("\n" + "-" * 50 + "\n")

  # 2. Perfil e Recorrência de Tutores e Cães
  df_recorrencia = con.execute(f"""
        SELECT 
            COALESCE("Hóspede", 'Não Identificado') AS tutor,
            COALESCE("Cão", 'Não Identificado') AS cao,
            COUNT(*) AS total_hospedagens,
            MIN("Entrada") AS primeira_hospedagem,
            MAX("Entrada") AS ultima_hospedagem
        FROM read_parquet('{silver_path}')
        GROUP BY 1, 2
        ORDER BY total_hospedagens DESC;
    """).df()

  print("--- 🐩 Frequência e Recorrência por Tutor / Cão ---")
  print(df_recorrencia.head(10))

  # Persistindo tabelas no DuckDB e Parquet
  con.execute(
      "CREATE OR REPLACE TABLE gold_financeiro_mensal AS SELECT * FROM"
      " df_financeiro"
  )
  con.execute(
      "CREATE OR REPLACE TABLE gold_recorrencia_clientes AS SELECT * FROM"
      " df_recorrencia"
  )

  df_financeiro.to_parquet(
      os.path.join(gold_dir, "gold_financeiro_mensal.parquet"), index=False
  )
  df_recorrencia.to_parquet(
      os.path.join(gold_dir, "gold_recorrencia_clientes.parquet"), index=False
  )

  con.close()
  print("\n✨ Métricas financeiras e de recorrência salvas com sucesso!")


if __name__ == "__main__":
  build_advanced_gold_metrics()