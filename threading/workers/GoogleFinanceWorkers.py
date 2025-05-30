import threading
import requests
from lxml import html
import time
import random

class GoogleFinancePriceWorker(threading.Thread):
    def __init__(self, symbol, **kwargs):
        super().__init__(**kwargs)

        self._symbol = symbol
        self._base_url = 'https://www.google.com/finance/quote/'
        self._url = f"{self._base_url}{self._symbol}:NSE"

        self.start()

    def run(self):
        # Start randomly after 0 to 30 s
        time.sleep(30 * random.random())
        r = requests.get(self._url)
        if r.status_code != 200:
            return
        page_contents = html.fromstring(r.text)
        price_x_path = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[4]/div/main/div[2]/div[1]/c-wiz/div/div[1]/div/div[1]/div/div[1]/div/span/div/div'
        price = float(page_contents.xpath(price_x_path)[0].text.replace('₹', '').replace(',',''))
        print(price)
