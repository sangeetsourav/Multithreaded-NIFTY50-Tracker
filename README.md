Multithreaded NIFTY50 Tracker
=============================

This is a multithreaded application which extracts the NIFTY50 symbols from Wikipedia, extracts the prices from Google 
Finance and stores the data in a Postgres database.

Run the following to start the application. It will print out worker and queue statistics while running.
```
python main.py
```

The environment.yml file specifies the conda environment used to develop this. 

The following environment variables must be set for the code to run
```
PG_DB (Postgres database name)
PG_HOST (Postgres IP)
PG_PW (Postgres password)
PG_USER (Postgres username)
PIPELINE_LOCATION (Path to the pipeline yaml file)
```
The [YamlPipelineExecutor](pipelines/yaml_reader.py) class is responsible for orchestrating all schedulers and worker threads. 

There are three schedulers in the application which are responsible for creating worker threads based on the parameters 
specified in the [pipeline](pipelines/wiki_google_scraper_pipeline.yml) .yml file

1. [WikiWorkerMasterScheduler](workers/WikiWorker.py): 
   1. It extracts NIFTY50 symbols from https://en.wikipedia.org/wiki/NIFTY_50.
   2. It is designed to use only 1 thread and puts the symbols in a thread-safe output queue which is accessed by its downstream worker GoogleFinanceWorker.

2. [GoogleFinancePriceScheduler](workers/GoogleFinanceWorker.py):
   1. It creates worker threads (as many as specified in `instances` in the .yml) which access the above output queue.
   2. These threads extract the price data for each symbol from https://www.google.com/finance/ and puts the data in a thread-safe output queue, which is accessed by its downstream worker PostgresWorker.

3. [PostgresMasterScheduler](workers/PostgresWorker.py):
   1. It creates worker threads (as many as specified in `instances` in the .yml) which access the above output queue.
   2. These threads write the data into a Postgres database.
