# ./tools/snp_mapper_local.py
import pandas as pd
import pysam
import json
from pathlib import Path
from tqdm import tqdm
from collections.abc import Iterable

# Caminhos
CSV_ENTRADA = "./data/261855.csv"
VCF_PATH = "/home/cosamores/mnt/dbsnp/GCF_000001405.40.gz"
OUTPUT_DIR = f"./resultados/snps_mapeados/dbsnp_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}"


# Carregar CSV
def carregar_csv(path):
    df = pd.read_csv(path, dtype=str)
    df = df.drop_duplicates(subset=["RSID"])
    return df

def parse_info(info):
    parsed = {}
    for k, v in info.items():
        if isinstance(v, bytes):
            parsed[k] = v.decode()
        elif isinstance(v, Iterable) and not isinstance(v, str):
            parsed[k] = list(v)
        else:
            parsed[k] = v
    return parsed

# Mapeamento local com pysam
def mapear_snps_locais(df, vcf_path):
    vcf = pysam.VariantFile(vcf_path)  # abre arquivo VCF indexado
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    for _, row in tqdm(df.iterrows(), total=len(df)):
        rsid = row["RSID"]

        try:
            # Busca por rsID direto no índice do VCF
            records = list(
                vcf.fetch(
                    contig=row["CHROMOSOME"],
                    start=int(row["POSITION"]) - 1,
                    end=int(row["POSITION"]),
                )
            )
            match = next((rec for rec in records if rec.id == rsid), None)

            if not match:
                print(f"❌ RSID {rsid} não encontrado.")
                continue

            # Criar JSON com campos desejados
            dados = {
                "rsid": rsid,
                "chromosome": row["CHROMOSOME"],
                "position": row["POSITION"],
                "ref": match.ref,
                "alt": list(match.alts) if match.alts is not None else [],
                "qual": match.qual,
                "filter": list(match.filter.keys()) if match.filter else [],
                "info": parse_info(match.info)
            }
            # Salvar JSON por RSID
            json_path = Path(OUTPUT_DIR) / f"{rsid}.json"
            with open(json_path, "w") as f:
                json.dump(dados, f, indent=2)

        except Exception as e:
            print(f"Erro processando {rsid}: {e}")


if __name__ == "__main__":
    df = carregar_csv(CSV_ENTRADA)
    mapear_snps_locais(df, VCF_PATH)
