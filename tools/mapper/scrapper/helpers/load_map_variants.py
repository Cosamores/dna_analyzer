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


def consultar_myvariant(rsid: str) -> dict:
    """
    Consulta MyVariant.info via API HTTP.
    Retorna dicionário com dados enriquecidos do SNP.
    """
    try:
        resp = httpx.get(f"{API_MYVARIANT}{rsid}", timeout=20)
        if resp.status_code == 200:
            dados = resp.json()

            gene = dados.get("dbsnp", {}).get("gene", {}).get("symbol", "")
            clin_sig = dados.get("clinvar", {}).get("clinical_significance", "")
            chrom = dados.get("dbsnp", {}).get("chrom", "")
            start = dados.get("dbsnp", {}).get("hg19", {}).get("start", "")
            ref = dados.get("dbsnp", {}).get("ref", "")
            alt = dados.get("dbsnp", {}).get("alt", "")
            vartype = dados.get("dbsnp", {}).get("vartype", "")
            trait_raw = dados.get("clinvar", {}).get("trait", "")
            if isinstance(trait_raw, list):
                # se for uma lista de strings ou dicts
                if trait_raw and isinstance(trait_raw[0], str):
                    trait = "; ".join(trait_raw)
                elif trait_raw and isinstance(trait_raw[0], dict):
                    trait = "; ".join(t.get("name", "") for t in trait_raw if isinstance(t, dict))
                else:
                    trait = ""
            else:
                trait = trait_raw
            effect = ""
            impact = ""

            # Dados do snpEff (se disponíveis)
            ann = dados.get("snpeff", {}).get("ann", [])
            if ann and isinstance(ann, list):
                effect = ann[0].get("effect", "")
                impact = ann[0].get("putative_impact", "")

            return {
                "gene": gene,
                "clin_sig": clin_sig,
                "chrom": chrom,
                "start": start,
                "ref": ref,
                "alt": alt,
                "vartype": vartype,
                "myvariant_trait": trait,
                "effect": effect,
                "impact": impact,
            }
    except Exception as e:
        print(f"Erro consultando {rsid}: {e}")
    return {}



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
