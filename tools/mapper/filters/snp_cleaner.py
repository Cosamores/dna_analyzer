from pathlib import Path
import json

import pandas as pd

def carregar_snps_filtrados(pasta: Path):
    snps_filtrados = []
    for arquivo in pasta.glob("*.json"):
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
            print(f"Carregando SNP: {dados.get('rsid', 'desconhecido')}")
            # Verifica se o arquivo contém dados relevantes
            if not dados:
                print(f"Arquivo {arquivo.name} está vazio ou não contém dados relevantes.")
                continue
            # Filtra por flags e texto relevante
            if (dados.get("found_snpedia_data") or dados.get("found_myvariant_data")):
                texto = dados.get("descricao_livre", "") + dados.get("resumo", "") + dados.get("trait", "")
                if texto.strip():
                    snps_filtrados.append(dados)
    return snps_filtrados


def extrair_alelos_relevantes(snp):
    alelo = snp["alelo"]
    alelos_relevantes = []

    for g in snp.get("genotipos", []):
        genotipo = g.get("genotipo", "")
        resumo = g.get("resumo", "").lower()
        if alelo in genotipo and "common" not in resumo and "normal" not in resumo:
            alelos_relevantes.append({
                "genotipo": genotipo,
                "resumo": resumo,
                "magnitude": g.get("magnitude")
            })
    return alelos_relevantes


if __name__ == "__main__":
    pasta = Path("resultados/2025-08-03_17-10-27")
    if not pasta.exists():
       print(f"A pasta {pasta} não existe.")
       exit(1)
    print(f"Carregando SNPs filtrados da pasta: {pasta}")

    snps_filtrados = carregar_snps_filtrados(pasta)
    print(f"Total SNPs filtrados: {len(snps_filtrados)}") # save the filtered snps jsons in the filtered_snps folder
    if snps_filtrados:
        pasta_filtrada = pasta / f"snps_filtrados_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        pasta_filtrada.mkdir(exist_ok=True)
        for snp in snps_filtrados:
            rsid = snp.get("rsid", "desconhecido")
            arquivo_filtrado = pasta_filtrada / f"{rsid}.json"
            with open(arquivo_filtrado, "w", encoding="utf-8") as f:
                json.dump(snp, f, ensure_ascii=False, indent=4)
        print(f"SNPs filtrados salvos na pasta: {pasta_filtrada}")
    else:
        print("Nenhum SNP filtrado encontrado.")