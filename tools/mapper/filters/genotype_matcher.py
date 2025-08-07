# ./tools/genotype_matcher.py

import os
import json
from pathlib import Path
import re
import pandas as pd

INPUT_DIR = Path(os.getenv("SNP_DATA_DIR", "resultados/2025-08-03_17-10-27/snps_filtrados_2025-08-06_16-34-54"))
OUTPUT_DIR = Path(os.getenv("RELEVANT_SNP_DIR", f"resultados/snps_com_alelos_relevantes_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def normalizar_genotipo(texto):
    """
    Transforma (A;G) ou rs123(A;T) em AG, mantendo ordem.
    """
    match = re.search(r'\(([ACGT\-];[ACGT\-])\)', texto)
    if match:
        letras = match.group(1).split(";")
        return "".join(sorted(letras))
    return ""

def extrair_alelos_de_texto(snp):
    """
    Extrai genótipos mencionados nos campos descritivos e verifica se coincidem com alelo_clean.
    """
    texto_completo = " ".join([
        snp.get("trait", ""),
        snp.get("resumo", ""),
        snp.get("descricao_livre", "")
    ])
    
    matches = re.findall(r'\(([ACGT\-];[ACGT\-])\)', texto_completo)
    alelos_texto = set("".join(sorted(m.split(";"))) for m in matches)

    if snp["alelo_clean"] in alelos_texto:
        return [{"fonte": "descricao_livre", "genotipo": snp["alelo_clean"], "resumo": texto_completo.strip()}]
    
    return []

def extrair_alelos_relevantes(snp):
    """
    Agora considera também genótipos citados nos textos, além dos da tabela.
    """
    alelo = snp.get("alelo")
    clean = snp.get("alelo_clean")
    relevantes = []

    for g in snp.get("genotipos", []):
        genotipo = g.get("genotipo", "")
        resumo = g.get("resumo", "").lower()
        if alelo in genotipo and "common" not in resumo and "normal" not in resumo:
            relevantes.append({
                "genotipo": genotipo,
                "resumo": resumo,
                "magnitude": g.get("magnitude", ""),
                "fonte": "tabela"
            })

    # Agora checamos também os campos descritivos
    relevantes += extrair_alelos_de_texto(snp)

    return relevantes

def filtrar_snps_com_alelos_relevantes(snps):
    """Filtra SNPs que tenham pelo menos um genótipo relevante para o alelo do indivíduo."""
    return [snp for snp in snps if extrair_alelos_relevantes(snp)]

def filtrar_e_salvar_snps_relevantes():
    total = 0
    salvos = 0

    for arquivo in INPUT_DIR.glob("*.json"):
        total += 1
        with open(arquivo, encoding="utf-8") as f:
            snp = json.load(f)

        relevantes = extrair_alelos_relevantes(snp)
        if not relevantes:
            continue

        snp["alelos_relevantes"] = relevantes

        output_path = OUTPUT_DIR / arquivo.name
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(snp, out, ensure_ascii=False, indent=2)

        salvos += 1

    print(f"\n✅ {salvos}/{total} SNPs salvos com alelos relevantes em: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    filtrar_e_salvar_snps_relevantes()
