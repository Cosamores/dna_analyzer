# DEPRECATED: Este arquivo será posteriormente integrado a main_pipeline.py

from operator import index
import pandas as pd
import requests
import time
from pathlib import Path

# ============ CONFIGURAÇÕES ============

CSV_ENTRADA = "261855.csv"
CSV_SAIDA = "analise_genetica_interpretada.csv"
ENDPOINT = "http://localhost:1234/v1/chat/completions"
MODELO = "akhilanilkumar_-_biogpt-baseline"

# ============ FUNÇÃO: MONTA PROMPT ============

def montar_prompt():
    return (
        f"Explique de forma clara e objetiva o impacto médico ou genético "
        f"de ter o genótipo GG na variante rsID rs1805009."
        f"Se não houver informação suficiente, responda 'Sem dados confiáveis disponíveis.'"
    )
    
    """ return (
        f"Explique de forma clara e objetiva o impacto médico ou genético "
        f"de ter o genótipo {genotipo} na variante rsID {rsid}. "
        f"Se não houver informação suficiente, responda 'Sem dados confiáveis disponíveis.'"
    ) """

# ============ FUNÇÃO: CONSULTA MODELO LOCAL ============

def consultar_biogpt(prompt):
    payload = {
        "model": MODELO,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 512,
        "stream": False
    }
    try:
        response = requests.post(ENDPOINT, json=payload, timeout=30)
        if response.ok:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            return f"[Erro HTTP {response.status_code}]"
    except Exception as e:
        return f"[Erro de conexão: {str(e)}]"

# ============ FLUXO PRINCIPAL ============

def processar_arquivo():
    # Verifica se o arquivo existe
   """  if not Path(CSV_ENTRADA).exists():
        print(f"Arquivo não encontrado: {CSV_ENTRADA}")
        return

    df = pd.read_csv(CSV_ENTRADA, dtype=str)

    if Path(CSV_SAIDA).exists():
        df_saida = pd.read_csv(CSV_SAIDA, dtype=str)
        rsids_processados = set(df_saida["RSID"])
        resultados = df_saida.to_dict(orient="records")
        print(f"✔ {len(rsids_processados)} variantes já processadas.")
    else:
        rsids_processados = set()
        resultados = []

    total = len(df)
    
    for index, row in df.iterrows():
        rsid = row["RSID"]
        genotipo = row["RESULT"]

        if rsid in rsids_processados:
            print(f"[({index}+{1})/{total}] {rsid} → já processado, pulando.")
            continue """

prompt = montar_prompt()

resposta = consultar_biogpt(prompt)

resultados = []

resultados.append({                  
        "PROMPT": prompt,
        "INTERPRETACAO": resposta
})
pd.DataFrame(resultados).to_csv(CSV_SAIDA, index=False)

time.sleep(0.5)  
print(f"\n🏁 Processamento finalizado. Total: {len(resultados)} variantes salvas em {CSV_SAIDA}")


# ============ EXECUÇÃO ============

if __name__ == "__main__":
    processar_arquivo()
