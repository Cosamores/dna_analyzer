# ./tools/snp_mapper.py
from bs4 import BeautifulSoup, Tag
from tools.load_map_variants import consultar_myvariant
from tools.snpedia_handler import SNPediaHandler

# ========== ETAPA 2: ENRIQUECIMENTO COM SNPEDIA ==========

def consultar_snpedia_completa(rsid: str, chromosome: str, position: int, alelo: str) -> dict:
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
        "found_myvariant_data": False
    }

    # 1) Extrai genótipos da tabela principal
    rows = soup.select('table.sortable.smwtable tbody tr')
    for tr in rows:
        if isinstance(tr, Tag):
            cols = tr.find_all('td')
            if len(cols) >= 3:
                geno = cols[0].get_text(strip=True)
                mag = cols[1].get_text(strip=True)
                desc = cols[2].get_text(strip=True)
                if geno or mag or desc:
                    data['genotipos'].append({
                        'genotipo': geno,
                        'magnitude': mag,
                        'resumo': desc
                    })
    if data['genotipos']:
        data['found_snpedia_data'] = True

    # 2) Extrai GMAF via célula <td>GMAF</nobr>
    gmaf_td = soup.find('td', string='GMAF')
    if isinstance(gmaf_td, Tag):
        gmaf_val_td = gmaf_td.find_next_sibling('td')
        if isinstance(gmaf_val_td, Tag):
            data['gmaf'] = gmaf_val_td.get_text(strip=True)
            data['found_snpedia_data'] = True

    # 3) Extrai Genes via célula <td>Gene</nobr>
    gene_td = soup.find('td', string='Gene')
    if isinstance(gene_td, Tag):
        gene_val_td = gene_td.find_next_sibling('td')
        if isinstance(gene_val_td, Tag):
            genes = [a.get_text(strip=True) for a in gene_val_td.find_all('a')]
            data['genes'] = genes
            if genes:
                data['found_snpedia_data'] = True

    # 4) Descrição livre: primeiro parágrafo com texto
    container = soup.select_one('div#mw-content-text div.mw-parser-output')
    if isinstance(container, Tag):
        paragraphs = container.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                data['descricao_livre'] = text
                data['found_snpedia_data'] = True
                break

    # Preenche trait e resumo
    if data['genotipos']:
        data['trait'] = data['genotipos'][0]['resumo']
    data['resumo'] = data['descricao_livre']

    # 5) MyVariant info
    gene, clin = consultar_myvariant(rsid)
    data['gene'] = gene
    data['significado_clinico'] = clin
    if gene or clin:
        data['found_myvariant_data'] = True

    return data
