import os
import duckdb

def build_gold_layer():
    silver_path = "data/silver/hospedagens_limpo.parquet"
    gold_dir = "data/gold"
    
    if not os.path.exists(silver_path):
        print(f"❌ Arquivo Silver não encontrado em {silver_path}. Execute a camada Silver primeiro!")
        return

    print("🚀 Iniciando processamento da Camada Gold com DuckDB...\n")
    os.makedirs(gold_dir, exist_ok=True)
    
    # Conecta ao DuckDB em memória (ou ao arquivo doghouse.duckdb)
    con = duckdb.connect("data/gold/doghouse.duckdb")

    # 1. Cria/Atualiza a View analítica principal apontando para o Parquet
    con.execute(f"""
        CREATE OR REPLACE VIEW stg_hospedagens AS 
        SELECT * FROM read_parquet('{silver_path}');
    """)

    # 2. Resumo de Formas de Pagamento (CORRIGIDO para forma_pagamento)
    print("--- 📊 1. Resumo por Forma de Pagamento ---")
    df_pagamentos = con.execute("""
        SELECT 
            COALESCE(forma_pagamento, 'Não Informado') AS forma_pagamento,
            COUNT(*) AS total_hospedagens
        FROM stg_hospedagens
        GROUP BY 1
        ORDER BY total_hospedagens DESC;
    """).df()
    print(df_pagamentos)
    print("\n" + "-"*50 + "\n")

    # 3. Top Cães/Hóspedes Frequentes (CORRIGIDO para nome_cao)
    print("--- 🐕 2. Top Hóspedes / Cães Frequentes ---")
    df_top_caes = con.execute("""
        SELECT 
            COALESCE(nome_cao, 'Não Identificado') AS nome_cao,
            COUNT(*) AS total_estadias
        FROM stg_hospedagens
        GROUP BY 1
        ORDER BY total_estadias DESC
        LIMIT 10;
    """).df()
    print(df_top_caes)
    print("\n" + "-"*50 + "\n")

    # 4. Salva as tabelas agregadas na camada Gold como arquivos Parquet e tabelas no banco DuckDB
    con.execute("CREATE OR REPLACE TABLE gold_resumo_pagamentos AS SELECT * FROM df_pagamentos")
    con.execute("CREATE OR REPLACE TABLE gold_top_caes AS SELECT * FROM df_top_caes")
    
    df_pagamentos.to_parquet(os.path.join(gold_dir, "gold_resumo_pagamentos.parquet"), index=False)
    df_top_caes.to_parquet(os.path.join(gold_dir, "gold_top_caes.parquet"), index=False)

    con.close()
    print(f"✨ Sucesso! Camada Gold processada. Banco de dados salvo em: data/gold/doghouse.duckdb")

if __name__ == "__main__":
    build_gold_layer()