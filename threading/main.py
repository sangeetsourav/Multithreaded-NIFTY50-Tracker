from workers.WikiWorker import WikiWorker
from workers.GoogleFinanceWorkers import GoogleFinancePriceScheduler
import time
from multiprocessing import Queue

# Declare queue of symboles
symbol_queue = Queue()

scraper_start_time = time.time()

# Wiki Worker instance
wiki_worker = WikiWorker()

# Get NIFTY 50 symbols
wiki_worker.get_nifty_50()

# Google Scheduler instance
num_google_finance_price_workers = 5
google_finance_price_scheduler_threads = []

for i in range(num_google_finance_price_workers):
    # Each instance starts running and waits for getting a value from the queue
    google_finance_price_scheduler = GoogleFinancePriceScheduler(input_queue=symbol_queue)

    google_finance_price_scheduler_threads.append(google_finance_price_scheduler)

for symbol in wiki_worker.symbols:
    symbol_queue.put(symbol)

for worker in google_finance_price_scheduler_threads:
    symbol_queue.put('DONE')

for worker in google_finance_price_scheduler_threads:
    worker.join()

print(f"Total extraction time: {round(time.time() - scraper_start_time,1)}")