import importlib
from multiprocessing import Queue

import yaml

class YamlPipelineExecutor:
    def __init__(self, pipeline_location):
        self._pipeline_location = pipeline_location
        self._queues = {}
        self._workers = {}

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

            if input_queue is not None:
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
        self._join_workers()
