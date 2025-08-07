# snp_reporter.py

from pathlib import Path
from collections import defaultdict, Counter
import json
import os
import pandas as pd

# ========== CONFIGURAÇÕES ==========
PASTA_SNP_INPUT = Path("resultados/snps_com_alelos_relevantes_2025-08-06_16-36-25")
PASTA_RELATORIOS = Path("resultados/estatisticas_snp_reporter") / pd.Timestamp.now().strftime("%Y-%m-%d_%H-%M-%S")
PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)

PALAVRAS_CHAVE_RISCO = ["cancer", "diabetes", "autism", "syndrome", "mutation", "Alzheimer", "cholesterol"]

# ========== FUNÇÕES AUXILIARES ==========
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

def salvar_md(nome_arquivo: str, linhas: list[str]):
    caminho = PASTA_RELATORIOS / f"{nome_arquivo}.md"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

def salvar_json(nome_arquivo: str, dados: dict):
    caminho = PASTA_RELATORIOS / f"{nome_arquivo}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ========== RELATÓRIOS BÁSICOS ==========
def relatorio_por_gene(snps):
    contagem = defaultdict(int)
    for snp in snps:
        genes = snp.get("genes", [])
        gene = snp.get("gene", "")
        for g in genes:
            contagem[g] += 1
        if gene and gene not in genes:
            contagem[gene] += 1
    return dict(sorted(contagem.items(), key=lambda x: x[1], reverse=True))

def relatorio_por_cromossomo(snps):
    contagem = Counter(snp.get("chromosome", "Desconhecido") for snp in snps)
    return dict(contagem)

def relatorio_por_genotipo(snps):
    contagem = Counter()
    for snp in snps:
        for g in snp.get("genotipos", []):
            contagem[g.get("genotipo", "?")] += 1
    return dict(contagem)

def relatorio_por_tipo_risco(snps):
    contagem = Counter()
    for snp in snps:
        texto = " ".join([snp.get("trait", ""), snp.get("resumo", ""), snp.get("descricao_livre", "")]).lower()
        for palavra in PALAVRAS_CHAVE_RISCO:
            if palavra in texto:
                contagem[palavra] += 1
    return dict(contagem)

# ========== RELATÓRIO CRUZADO ==========
def cruzar_genes_com_riscos(snps):
    genes_por_risco = defaultdict(list)
    for snp in snps:
        texto = " ".join([snp.get("trait", ""), snp.get("resumo", ""), snp.get("descricao_livre", "")]).lower()
        for risco in PALAVRAS_CHAVE_RISCO:
            if risco in texto:
                genes = snp.get("genes", []) + [snp.get("gene", "")]
                for g in genes:
                    if g:
                        genes_por_risco[risco].append(g)
    return {
        risco: dict(Counter(genes).most_common())
        for risco, genes in genes_por_risco.items()
    }

# ========== EXECUÇÃO PRINCIPAL ==========
snps = carregar_snps(PASTA_SNP_INPUT)
print(f"✅ {len(snps)} SNPs carregados para análise.")

relatorios = {
    "genes": relatorio_por_gene(snps),
    "cromossomos": relatorio_por_cromossomo(snps),
    "genotipos": relatorio_por_genotipo(snps),
    "tipos_risco": relatorio_por_tipo_risco(snps),
    "cruzamento_genes_riscos": cruzar_genes_com_riscos(snps),
}

for nome, dados in relatorios.items():
    salvar_json(nome, dados)
    salvar_md(nome, [f"# Relatório: {nome}\n"] + [f"- {k}: {v}" for k, v in dados.items()])

print(f"📊 Relatórios gerados em: {PASTA_RELATORIOS.resolve()}")
