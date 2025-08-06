# ./tools/snpedia_handler.py
import mwclient
import httpx
from bs4 import BeautifulSoup
from typing import List


class SNPediaHandler:
    def __init__(self, api_url: str = 'bots.snpedia.com', path: str = '/'):
        self.site = mwclient.Site(api_url, path=path)

    def list_all_snps(self) -> List[str]:
        """
        Retorna lista de todas as páginas de SNP existentes na categoria 'Is_a_snp'.
        """
        cat = self.site.Categories['Is_a_snp']
        return [page.name for page in cat]

    def exists(self, rsid: str) -> bool:
        """
        Verifica se a página de um SNP existe em SNPedia (HTTP 200).
        """
        try:
            page = self.site.pages[rsid]
            text = page.text()
            return bool(text and 'rs' in rsid.lower())
        except Exception:
            return False

    def fetch_html(self, rsid: str) -> str:
        """
        Roda request HTTP direto para obter HTML renderizado.
        """
        url = f'https://www.snpedia.com/index.php/{rsid}'
        # recomendamos usar requests para HTML completo
        resp = httpx.get(url, timeout=50)
        resp.raise_for_status()
        return resp.text
