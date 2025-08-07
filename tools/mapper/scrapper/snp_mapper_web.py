# ./tools/snp_mapper.py
from bs4 import BeautifulSoup, Tag
from tools.mapper.scrapper.helpers.load_map_variants import consultar_myvariant
from tools.mapper.scrapper.helpers.snpedia_handler import SNPediaHandler
from tools.mapper.scrapper.snp_locator import consultar_localizacao_ensembl

# ========== ETAPA 2: ENRIQUECIMENTO COM SNPEDIA ==========


def consultar_snpedia_completa(
    rsid: str, chromosome: str, position: int, alelo: str
) -> dict:
    """
    Consulta a página HTML da SNPedia e extrai:
      - genótipos (geno, magnitude, resumo)
      - genes listados
      - GMAF
      - descrição livre
    Combina com dados de MyVariant e marca origem dos dados.
    """
    rsid = rsid.strip()
    rsid = rsid[0].upper() + rsid[1:].lower() if rsid.lower().startswith("rs") else rsid

    handler = SNPediaHandler()
    html = handler.fetch_html(rsid)
    soup = BeautifulSoup(html, "html.parser")

    data = {
        "rsid": rsid,
        "chromosome": chromosome,
        "position": position,
        "alelo": f"{alelo[0]};{alelo[1]}" if len(alelo) == 2 else alelo,
        "alelo_clean": alelo,
        "genotipos": [],
        "gmaf": None,
        "genes": [],
        "descricao_livre": "",
        "trait": "",
        "resumo": "",
        "url": f"https://www.snpedia.com/index.php/{rsid}",
        # flags
        "found_snpedia_data": False,
        "found_myvariant_data": False,
    }

    # 1) Extrai genótipos da tabela principal
    rows = soup.select("table.sortable.smwtable tbody tr")
    for tr in rows:
        if isinstance(tr, Tag):
            cols = tr.find_all("td")
            if len(cols) >= 3:
                geno = cols[0].get_text(strip=True)
                mag = cols[1].get_text(strip=True)
                desc = cols[2].get_text(strip=True)
                if geno or mag or desc:
                    data["genotipos"].append(
                        {"genotipo": geno, "magnitude": mag, "resumo": desc}
                    )
    if data["genotipos"]:
        data["found_snpedia_data"] = True

    # 2) Extrai GMAF via célula <td>GMAF</nobr>
    gmaf_td = soup.find("td", string="GMAF")
    if isinstance(gmaf_td, Tag):
        gmaf_val_td = gmaf_td.find_next_sibling("td")
        if isinstance(gmaf_val_td, Tag):
            data["gmaf"] = gmaf_val_td.get_text(strip=True)
            data["found_snpedia_data"] = True

    # 3) Extrai Genes via célula <td>Gene</nobr>
    gene_td = soup.find("td", string="Gene")
    if isinstance(gene_td, Tag):
        gene_val_td = gene_td.find_next_sibling("td")
        if isinstance(gene_val_td, Tag):
            genes = [a.get_text(strip=True) for a in gene_val_td.find_all("a")]
            data["genes"] = genes
            if genes:
                data["found_snpedia_data"] = True

    # 4) Descrição livre: primeiro parágrafo com texto
    container = soup.select_one("div#mw-content-text div.mw-parser-output")
    if isinstance(container, Tag):
        paragraphs = container.find_all("p")
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                data["descricao_livre"] = text
                data["found_snpedia_data"] = True
                break

    # Preenche trait e resumo
    if data["genotipos"]:
        data["trait"] = data["genotipos"][0]["resumo"]
    data["resumo"] = data["descricao_livre"]

    # 5) MyVariant info (dados estendidos)
    myvariant_data = consultar_myvariant(rsid)


    if myvariant_data:
        data.update(
            {
            "gene": myvariant_data.get("gene", ""),
            "significado_clinico": myvariant_data.get("clin_sig", ""),
            "ref": myvariant_data.get("ref", ""),
            "alt": myvariant_data.get("alt", ""),
            "vartype": myvariant_data.get("vartype", ""),
            "myvariant_trait": myvariant_data.get("trait", ""),
            "effect": myvariant_data.get("effect", ""),
            "putative_impact": myvariant_data.get("impact", ""),
            }
        )
    
        data["found_myvariant_data"] = True

    # 6) Ensembl VEP: informações funcionais
    info_funcional = consultar_localizacao_ensembl(rsid, chromosome, position)

    if info_funcional:
        data["location_type"] = info_funcional.get("location_type", "")
        data["region"] = info_funcional.get("region", "")
        data["impact"] = info_funcional.get("impact", "")
        data["variant_consequence"] = info_funcional.get("variant_consequence", "")
        data["regulatory_effect"] = info_funcional.get("regulatory_effect", "")
        data["found_ensembl_data"] = True
    else:
        data["found_ensembl_data"] = False

    return data
