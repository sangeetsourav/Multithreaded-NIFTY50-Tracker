from workers.WikiWorker import WikiWorker
from workers.GoogleFinanceWorkers import GoogleFinancePriceScheduler
from workers.PostgreWorker import PostgresMasterScheduler
import time
from multiprocessing import Queue

# Declare queue of symbols
symbol_queue = Queue()
db_data_queue = Queue()

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
    google_finance_price_scheduler = GoogleFinancePriceScheduler(input_queue=symbol_queue, output_queues=[db_data_queue])

    google_finance_price_scheduler_threads.append(google_finance_price_scheduler)

# Postgres Scheduler instance
num_postgres_workers = 10
postgres_scheduler_threads = []

for i in range(num_postgres_workers):
    # Each instance starts running and waits for getting a value from the queue
    postgres_scheduler = PostgresMasterScheduler(input_queue=db_data_queue)

    postgres_scheduler_threads.append(postgres_scheduler)

# Add the symbols in queue
for symbol in wiki_worker.symbols:
    symbol_queue.put(symbol)

# Join back threads into main thread
for worker in google_finance_price_scheduler_threads:
    worker.join()

# Join back threads into main thread
for worker in postgres_scheduler_threads:
    worker.join()

print(f"Total time: {round(time.time() - scraper_start_time,1)}")