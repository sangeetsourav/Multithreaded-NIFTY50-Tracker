import importlib
import time
from multiprocessing import Queue
import threading

import yaml

class YamlPipelineExecutor(threading.Thread):
    def __init__(self, pipeline_location):
        super().__init__()
        self._pipeline_location = pipeline_location
        self._queues = {}
        self._workers = {}
        # Queue - Number of worker threads
        # Assumed that there is only one worker per queue
        self._queue_consumers = {}

        # Worker Name - Output Queue
        self._downstream_queues = {}

    def _load_pipeline(self):
        with open(self._pipeline_location, 'r') as f:
            self._yaml_data = yaml.safe_load(f)

    def _initialize_queues(self):
        for queue in self._yaml_data['queues']:
            self._queues[queue['name']] = Queue()

    def _initialize_workers(self):
        for worker in self._yaml_data['workers']:
            worker_name = worker['name']

            num_instances = worker.get('instances', 1)

            # Get the class through importlib
            worker_class = getattr(importlib.import_module(worker['location']), worker['class'])

            # .get() because input_queue/output_queues/input_values might not be defined
            input_queue = worker.get("input_queue")
            output_queues = worker.get('output_queues')
            input_values = worker.get('input_values')

            self._downstream_queues[worker_name] = output_queues

            if input_queue is not None:
                self._queue_consumers[input_queue] = num_instances
                input_queue = self._queues[worker.get("input_queue")]

            if output_queues is not None:
                output_queues = [self._queues[x] for x in output_queues]

            self._workers[worker_name] = []
            for i in range(num_instances):
                self._workers[worker_name].append(worker_class(input_queue=input_queue,
                                                               output_queues=output_queues,
                                                               input_values=input_values))

    def _join_workers(self):
        for worker_name, worker_threads in self._workers.items():
            for worker_thread in worker_threads:
                worker_thread.join()

    def process_pipeline(self):
        self._load_pipeline()
        self._initialize_queues()
        self._initialize_workers()
        # We don't need to join the worker threads as the self.run()
        # is going to be alive until all worker threads are done

    def run(self):
        self.process_pipeline()
        # Monitor and send DONE to downstream workers
        while True:
            total_workers_alive = 0
            worker_stats = []
            q_stats = []
            worker_del = []
            for worker_name, worker_threads in self._workers.items():
                total_worker_threads_alive = 0
                for worker_thread in worker_threads:
                    if worker_thread.is_alive():
                        total_worker_threads_alive += 1

                if total_worker_threads_alive == 0:
                    if self._downstream_queues[worker_name] is not None:
                        for output_queue in self._downstream_queues[worker_name]:
                            num_downstream_worker_threads = self._queue_consumers[output_queue]

                            for i in range(num_downstream_worker_threads):
                                self._queues[output_queue].put('DONE')

                    worker_del.append(worker_name)

                else:
                    total_workers_alive += 1

                worker_stats.append([worker_name, total_worker_threads_alive])

            # As all worker threads have ended, we remove this from the dictionary of works
            for worker in worker_del:
                del self._workers[worker]

            for queue in self._queues:
                q_stats.append([queue, self._queues[queue].qsize()])

            print("Queue Stats: ",q_stats)
            print("Worker Stats: ",worker_stats)

            if total_workers_alive == 0:
                break

            time.sleep(5)
