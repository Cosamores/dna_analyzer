# ./tools/genotype_matcher.py

import os
import json
from pathlib import Path

INPUT_DIR = Path(os.getenv("SNP_DATA_DIR", "resultados/snps_filtrados"))
OUTPUT_DIR = Path(os.getenv("RELEVANT_SNP_DIR", "resultados/snps_com_alelos_relevantes"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extrair_alelos_relevantes(snp):
    """Retorna genótipos relevantes (não comuns
    /normais) que casam com o alelo do indivíduo."""
    alelo = snp.get("alelo")
    relevantes = []
    for g in snp.get("genotipos", []):
        genotipo = g.get("genotipo", "")
        resumo = g.get("resumo", "").lower()
        if alelo in genotipo and "common" not in resumo and "normal" not in resumo:
            relevantes.append({
                "genotipo": genotipo,
                "resumo": resumo,
                "magnitude": g.get("magnitude", "")
            })
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
