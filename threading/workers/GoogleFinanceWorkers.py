import threading
import requests
from lxml import html
import time
import random

class GoogleFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue, **kwargs):
        super().__init__(**kwargs)
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            # get() keeps waiting until the queue returns value
            # If the queue is initially empty then this method wil keep waiting
            val = self._input_queue.get()
            if val == 'DONE':
                break

            yahoo_finance_price_worker = GoogleFinancePriceWorker(symbol=val)
            price = yahoo_finance_price_worker.get_price()
            print(f"{val}: {price}")
            time.sleep(random.random())

class GoogleFinancePriceWorker:
    def __init__(self, symbol):
        self._symbol = symbol
        self._base_url = 'https://www.google.com/finance/quote/'
        self._url = f"{self._base_url}{self._symbol}:NSE"

    def get_price(self):
        r = requests.get(self._url)
        if r.status_code != 200:
            return
        page_contents = html.fromstring(r.text)
        price_x_path = '//*[@id="yDmH0d"]/c-wiz[2]/div/div[4]/div/main/div[2]/div[1]/c-wiz/div/div[1]/div/div[1]/div/div[1]/div/span/div/div'
        price = float(page_contents.xpath(price_x_path)[0].text.replace('₹', '').replace(',',''))

        return price
