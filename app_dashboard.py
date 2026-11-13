import duckdb
import pandas as pd
import streamlit as st

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="DogHouse Lakehouse Dashboard", page_icon="🐶", layout="wide"
)

st.title("🐶 DogHouse Lakehouse — Painel Executivo")
st.markdown(
    "Monitoramento de métricas e indicadores da creche canina baseado na"
    " Arquitetura Medallion."
)


# Função para conectar e ler os dados da Camada Gold via DuckDB
@st.cache_data
def load_gold_data():
  conn = duckdb.connect("data/gold/doghouse.duckdb", read_only=True)

  # Listar tabelas disponíveis
  tables = conn.execute("SHOW TABLES").fetchall()
  table_names = [t[0] for t in tables]

  data = {}
  for table in table_names:
    data[table] = conn.execute(f"SELECT * FROM {table}").df()

  conn.close()
  return data


# Carregar os dados
try:
  gold_data = load_gold_data()

  # Sidebar para navegação
  st.sidebar.header("Filtros & Navegação")
  pagina = st.sidebar.selectbox(
      "Escolha a Visão", ["Visão Geral & KPIs", "Dados Detalhados"]
  )

  if pagina == "Visão Geral & KPIs":
    st.subheader("📊 Indicadores Principais (Camada Gold)")

    # Exibir métricas principais se as tabelas existirem
    col1, col2 = st.columns(2)

    if "resumo_pagamento" in gold_data:
      with col1:
        st.markdown("### Forma de Pagamento")
        df_pagamento = gold_data["resumo_pagamento"]
        st.dataframe(df_pagamento, use_container_width=True)
        st.bar_chart(df_pagamento.set_index("forma_pagamento"))

    if "top_caes" in gold_data:
      with col2:
        st.markdown("### 🐕 Top Cães Frequentes")
        df_caes = gold_data["top_caes"]
        st.dataframe(df_caes, use_container_width=True)
        st.bar_chart(df_caes.set_index("nome_cao"))

  elif pagina == "Dados Detalhados":
    st.subheader("📂 Tabelas Brutas na Camada Gold")
    for name, df in gold_data.items():
      st.markdown(f"**Tabela: `{name}`**")
      st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error(
      "⚠️ Erro ao carregar os dados da camada Gold. Certifique-se de executar o"
      f" pipeline (`python main.py`) primeiro.\n\nDetalhes: {e}"
  )