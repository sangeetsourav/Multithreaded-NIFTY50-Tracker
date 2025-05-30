import requests
from bs4 import BeautifulSoup
import threading

class WikiWorker:
    def __init__(self):
        self._url = "https://en.wikipedia.org/wiki/NIFTY_50"
        self.symbols = []

    def _extract_company_symbols(self, page_html):
        soup = BeautifulSoup(markup=page_html, features="lxml")
        table = soup.find(id='constituents')
        table_rows = table.find_all('tr')

        # Skip the first one since it will be the header
        for row in table_rows[1:]:
            symbol = row.find_all('td')[1].text.strip()
            self.symbols.append(symbol)

    def get_nifty_50(self):
        response = requests.get(self._url)

        if response.status_code != 200:
            print("Couldn't fetch data")
        else:
            self._extract_company_symbols(page_html=response.text)
