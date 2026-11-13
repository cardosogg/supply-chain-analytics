import json
import os
import random
from datetime import datetime, timedelta

# Nomes fictícios de cães e formas de pagamento para simulação
CAES_EXEMPLO = ["Thor", "Luna", "Mel", "Bob", "Zeus", "Cacau", "Pipoca", "Amora"]
FORMAS_PAGAMENTO = ["Pix", "Dinheiro", "Cartão de Crédito", "Não Informado"]

def generate_mock_hospedagens(count=10):
    """Gera dados sintéticos simulando o retorno da API do Notion."""
    results = []
    base_date = datetime.now()

    for i in range(count):
        data_entrada = base_date - timedelta(days=random.randint(1, 30))
        dias_hospedagem = random.randint(1, 7)
        data_saida = data_entrada + timedelta(days=dias_hospedagem)
        
        # Estrutura JSON padrão retornada pela API do Notion
        page = {
            "id": f"mock-id-{i+1:03d}",
            "properties": {
                "Nome": {
                    "title": [{"text": {"content": random.choice(CAES_EXEMPLO)}}]
                },
                "Data Entrada": {
                    "date": {"start": data_entrada.strftime("%Y-%m-%d")}
                },
                "Data Saída": {
                    "date": {"start": data_saida.strftime("%Y-%m-%d")}
                },
                "Forma de Pagamento": {
                    "select": {"name": random.choice(FORMAS_PAGAMENTO)}
                },
                "Valor Total": {
                    "number": round(random.uniform(100.0, 800.0), 2)
                }
            }
        }
        results.append(page)
    
    return {"results": results}

if __name__ == "__main__":
    mock_data = generate_mock_hospedagens()
    os.makedirs("data/bronze", exist_ok=True)
    with open("data/bronze/raw_hospedagens.json", "w", encoding="utf-8") as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=4)
    print("✨ Dados sintéticos gerados com sucesso em data/bronze/raw_hospedagens.json!")