import threading
import time
import random

import requests
from bs4 import BeautifulSoup

class WikiWorkerMasterScheduler(threading.Thread):
    def __init__(self, input_queue, output_queues, input_values, **kwargs):
        super().__init__(**kwargs)
        self._input_values = input_values

        if not isinstance(output_queues, list):
            self._output_queues = [output_queues]

        self._output_queues = output_queues
        self.start()

    def run(self):
        for url in self._input_values:
            wiki_worker = WikiWorker(url)
            wiki_worker.get_nifty_50()

            for output_queue in self._output_queues:
                for symbol in wiki_worker.symbols:
                    output_queue.put(symbol)

            time.sleep(random.random())

        print("Wiki Worker has completed.")


class WikiWorker:
    def __init__(self, url):
        self._url = url
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
