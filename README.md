Multithreaded NIFTY50 Tracker
=============================

This is a multithreaded application which extracts the NIFTY50 symbols from Wikipedia, extracts the prices from Google 
Finance and stores the data in a Postgres database.

Run main.py to run the application. The environment.yml file specifies the conda environment used to develop this. 

The following environment variables must be set for the code to run
1. PG_DB (Postgres database name)
2. PG_HOST (Postgres IP)
3. PG_PW (Postgres password)
4. PG_USER (Postgres username)
5. PIPELINE_LOCATION (Path to the pipeline yaml file)

The pipeline .yml file is responsible for orchestrating all schedulers and worker threads. This is done through 
the YamlPipelineExecutor class in yaml_reader.py.

There are three schedulers in the application which are responsible to create worker threads based on the parameters 
specified in the pipeline .yml file

1. WikiWorkerMasterScheduler: 
   1. It extracts NIFTY50 symbols from https://en.wikipedia.org/wiki/NIFTY_50.
   2. It is designed to use only 1 thread and puts the symbols in a thread-safe output queue which is accessed by downstream workers.
2. GoogleFinancePriceScheduler:
   1. It creates worker threads (as many as specified in `instances` in the .yml) which access the above output queue.
   2. These threads extract the price data for each symbol from https://www.google.com/finance/ and puts the data in a thread-safe output queue.
3. PostgresMasterScheduler:
   1. It creates worker threads (as many as specified in `instances` in the .yml) which access the above output queue.
   2. These threads write the data into a Postgres database.