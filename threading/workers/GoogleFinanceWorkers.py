import time
import datetime
import random
from queue import Empty
import threading

import requests
from lxml import html

class GoogleFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue, output_queues, input_values, **kwargs):
        super().__init__(**kwargs)
        self._input_queue = input_queue

        if not isinstance(output_queues,list):
            self._output_queues = [output_queues]

        self._output_queues = output_queues
        self.start()

    def run(self):
        while True:
            try:
                # get() keeps waiting until the queue returns value, so we add a timeout
                val = self._input_queue.get(timeout=10)
            except Empty:
                print("Google finance worker timed out.")
                break

            yahoo_finance_price_worker = GoogleFinancePriceWorker(symbol=val)
            price = yahoo_finance_price_worker.get_price()
            for output_queue in self._output_queues:
                output_values = (val, price, datetime.datetime.now(datetime.UTC))
                output_queue.put(output_values)
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
