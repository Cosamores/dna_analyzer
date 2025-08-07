from pathlib import Path
from collections import defaultdict
import json
import pandas as pd

# === CONFIG ===
PASTA_SNP_INPUT = Path("resultados/snps_com_alelos_relevantes_2025-08-06_16-36-25")
PASTA_RELATORIOS = Path("resultados/estatisticas_snp_reporter") / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

FATORES_RISCO = ["cancer", "diabetes", "autism", "syndrome", "mutation", "alzheimer", "cholesterol"]

# === FUNÇÕES ===
def carregar_snps(diretorio: Path):
    snps = []
    for arquivo in diretorio.glob("*.json"):
        with open(arquivo, encoding="utf-8") as f:
            try:
                snp = json.load(f)
                snps.append(snp)
            except Exception as e:
                print(f"Erro ao carregar {arquivo.name}: {e}")
    return snps

def gerar_cruzamento_detalhado(snps):
    cruzamento = defaultdict(lambda: defaultdict(list))

    for snp in snps:
        texto = " ".join([
            snp.get("trait", ""),
            snp.get("resumo", ""),
            snp.get("descricao_livre", "")
        ]).lower()

        rsid = snp.get("rsid", "?")
        gene = snp.get("gene") or (snp.get("genes") or [None])[0]
        cromossomo = snp.get("chromosome")
        posicao = snp.get("position")
        alelo = snp.get("alelo_clean", "")

        for risco in FATORES_RISCO:
            if risco in texto:
                cruzamento[risco][gene].append({
                    "rsid": rsid,
                    "chromosome": cromossomo,
                    "position": posicao,
                    "genotype": alelo
                })

    return cruzamento

def salvar_md_e_json(nome, cruzamento):
    md_path = PASTA_RELATORIOS / f"{nome}.md"
    json_path = PASTA_RELATORIOS / f"{nome}.json"

    with open(md_path, "w", encoding="utf-8") as f:
        for risco, genes in cruzamento.items():
            f.write(f"# Fator de Risco: {risco}\n\n")
            f.write(f"## Genes associados:\n")
            for gene in genes:
                f.write(f"- {gene}\n")
            f.write(f"\n## SNPs envolvidos:\n")
            f.write("| RSID | Gene | Cromossomo | Posição | Genótipo |\n")
            f.write("|------|------|-------------|-----------|----------|\n")
            for gene, snps in genes.items():
                for snp in snps:
                    f.write(f"| {snp['rsid']} | {gene} | {snp['chromosome']} | {snp['position']} | {snp['genotype']} |\n")
            f.write("\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cruzamento, f, ensure_ascii=False, indent=2)

# === EXECUÇÃO ===
snps = carregar_snps(PASTA_SNP_INPUT)
print(f"✅ {len(snps)} SNPs carregados.")

cruzamento = gerar_cruzamento_detalhado(snps)
salvar_md_e_json("cruzamento_risco_detalhado", cruzamento)

print(f"📄 Relatório 'cruzamento_risco_detalhado' salvo em: {PASTA_RELATORIOS.resolve()}")
