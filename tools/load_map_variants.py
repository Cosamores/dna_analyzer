# ./tools/load_map_variants.py
import pandas as pd
import httpx
from tqdm import tqdm
from pathlib import Path
from config.env import API_MYVARIANT, CSV_ENTRADA, CSV_SAIDA

# ========== ETAPA 1: LEITURA E MAPEAMENTO BÁSICO MyVariant ==========

def carregar_csv(caminho: str) -> pd.DataFrame:
    df = pd.read_csv(caminho, dtype=str)
    df = df.drop_duplicates(subset=["RSID"])
    df = df[["RSID", "CHROMOSOME", "POSITION", "RESULT"]]
    return df.reset_index(drop=True)


def consultar_myvariant(rsid: str) -> tuple[str, str]:
    """
    Consulta MyVariant.info via API HTTP (requests).
    Retorna (gene_symbol, clinical_significance).
    """
    try:
        resp =  httpx.get(f"{API_MYVARIANT}{rsid}", timeout=50)
        if resp.status_code == 200:
            dados = resp.json()
            gene = dados.get("dbsnp", {}).get("gene", {}).get("symbol", "")
            clin = dados.get("clinvar", {}).get("clinical_significance", "")
            return gene, clin
    except Exception:
        pass
    return "", ""


def mapear_variantes(df: pd.DataFrame) -> pd.DataFrame:
    genes, clins = [], []
    for rsid in tqdm(df["RSID"], desc="Mapeando MyVariant"):
        gene, clin = consultar_myvariant(rsid)
        genes.append(gene)
        clins.append(clin)
    df["GENE"] = genes
    df["SIGNIFICADO_CLINICO"] = clins
    return df


if __name__ == "__main__":
    if not Path(CSV_ENTRADA).exists():
        print(f"❌ CSV de entrada não encontrado: {CSV_ENTRADA}")
        exit(1)
    df = carregar_csv(CSV_ENTRADA)
    df2 = mapear_variantes(df)
    df2.to_csv(CSV_SAIDA, index=False)
    print(f"✅ MyVariant mapeamento salvo em: {CSV_SAIDA}")
