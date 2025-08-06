# ./utils/json_tools.py

from pathlib import Path
import json

def snp_ja_processado(rsid: str, pasta_saida: Path) -> bool:
    return (pasta_saida / f"{rsid}.json").exists()

def salvar_json_snp(rsid: str, dados: dict, pasta_saida: Path):
    caminho = pasta_saida / f"{rsid}.json"
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
