import os
from dotenv import load_dotenv

load_dotenv()

CSV_ENTRADA = os.getenv("CSV_ENTRADA", "./data/261855.csv")
CSV_SAIDA = os.getenv("CSV_SAIDA", "variants_com_mapeamentoNEW.csv")
CACHE_FILE = os.getenv("CACHE_FILE", "variant_cacheNEW.pkl")
API_MYVARIANT = os.getenv("API_MYVARIANT", "https://myvariant.info/v1/variant/")
URL_SNEDIA = os.getenv("URL_SNEDIA", "https://www.snpedia.com/index.php/")
SNP_MAPPING_SAIDA = os.getenv("SNP_MAPPING_SAIDA", "snps_data")
ENSEMBL_REST_API = os.getenv("ENSEMBL_REST_API", "https://rest.ensembl.org")
