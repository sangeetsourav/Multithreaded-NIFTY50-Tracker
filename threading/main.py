import os
import time

from yaml_reader import YamlPipelineExecutor

def main():
    scraper_start_time = time.time()

    pipeline_location = os.environ.get('PIPELINE_LOCATION')

    if pipeline_location is None:
        print("Please set PIPELINE_LOCATION environment variable")
        exit()

    yaml_pipeline_executor = YamlPipelineExecutor(pipeline_location=pipeline_location)
    yaml_pipeline_executor.start()
    yaml_pipeline_executor.join()

    print(f"Total time: {round(time.time() - scraper_start_time,1)}s")


if __name__ == "__main__":
    main()