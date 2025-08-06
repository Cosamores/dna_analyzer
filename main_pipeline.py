# ./main_pipeline.py
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from config.env import CSV_ENTRADA
from tools.snp_mapper import consultar_snpedia_completa
from utils.json_tools import snp_ja_processado, salvar_json_snp

# ====== CONFIGURAÇÕES ======


PASTA_SAIDA = Path("resultados/snp_mapping_data") / pd.Timestamp.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

# ====== EXECUÇÃO PRINCIPAL ======


def main():
    # Verifica CSV de entrada
    if not Path(CSV_ENTRADA).exists():
        print(f"❌ CSV de entrada não encontrado: {CSV_ENTRADA}")
        exit(1)

    # Carrega lista única de RSIDs
    df = pd.read_csv(CSV_ENTRADA, dtype=str)


    if not all(col in df.columns for col in ["RSID", "CHROMOSOME", "POSITION", "RESULT"]):
      print("❌ Colunas esperadas não encontradas no CSV.")
      return

    # Processa cada linha
    for rsid, chrom, pos, alelo in tqdm(
      zip(df["RSID"], df["CHROMOSOME"], df["POSITION"], df["RESULT"]),
      total=len(df),
      desc="Processando SNPs",
      unit="SNP"):
      if snp_ja_processado(rsid, PASTA_SAIDA):
        continue
      try:
          dados = consultar_snpedia_completa(rsid, chrom, pos, alelo)
          salvar_json_snp(rsid, dados, PASTA_SAIDA)
      except Exception as e:
        print(f"⚠️ Erro ao processar {rsid}: {e}")
    
    print(f"\n✅ Pipeline finalizado. JSONs em: {PASTA_SAIDA.resolve()}")

if __name__ == "__main__":
    main()
