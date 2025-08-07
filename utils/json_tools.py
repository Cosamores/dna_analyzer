# ./utils/json_tools.py

from pathlib import Path
import json

def snp_ja_processado(rsid: str, pasta_saida: Path) -> bool:
    return (pasta_saida / f"{rsid}.json").exists()

def salvar_json_snp(rsid: str, dados: dict, pasta_saida: Path):
    caminho = pasta_saida / f"{rsid}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

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

def salvar_md(nome_arquivo: str, linhas: list[str], pasta_saida: Path):
    caminho = pasta_saida / f"{nome_arquivo}.md"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

def salvar_json(nome_arquivo: str, dados: dict, pasta_saida: Path):
    caminho = pasta_saida / f"{nome_arquivo}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
