from workers.WikiWorker import WikiWorker
from workers.GoogleFinanceWorkers import GoogleFinancePriceWorker
import time

scraper_start_time = time.time()

wiki_worker = WikiWorker()
wiki_worker.get_nifty_50()

current_workers = []
for symbol in wiki_worker.symbols:
    google_finance_price_worker = GoogleFinancePriceWorker(symbol=symbol)
    current_workers.append(google_finance_price_worker)

for worker in current_workers:
    worker.join()

print(f"Total extraction time: {round(time.time() - scraper_start_time,1)}")