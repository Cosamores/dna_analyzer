# ./tools/snp_locator.py
import httpx
from typing import Optional
from config.env import ENSEMBL_REST_API

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

def consultar_localizacao_ensembl(rsid: str, chromosome: str, position: int) -> Optional[dict]:
    """
    Consulta a Ensembl REST API para obter dados funcionais e estruturais de um SNP por rsid.
    Retorna um dicionário com tipo de localização, região funcional, impacto e efeito.
    """
    try:
        url = f"{ENSEMBL_REST_API}/vep/human/id/{rsid}?content-type=application/json"
        response = httpx.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        # Normalmente o primeiro elemento traz os dados principais
        info = data[0]

        # Consequências moleculares
        consequence_terms = info.get("most_severe_consequence", "")
        impact = info.get("transcript_consequences", [{}])[0].get("impact", "")
        gene_symbol = info.get("transcript_consequences", [{}])[0].get("gene_symbol", "")

        region = info.get("regulatory_feature_consequences", [{}])[0].get("biotype", "")
        regulatory_effect = info.get("regulatory_feature_consequences", [{}])[0].get("consequence_terms", [])

        return {
            "variant_consequence": consequence_terms,
            "impact": impact,
            "region": region,
            "regulatory_effect": ", ".join(regulatory_effect),
            "location_type": info.get("colocated_variants", [{}])[0].get("variant_class", ""),
        }

    except Exception as e:
        print(f"[Ensembl] Erro ao consultar {rsid}: {e}")
        return None
