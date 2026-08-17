import dlt
import requests
import os
from dotenv import load_dotenv

load_dotenv()

@dlt.resource(name="router_logs", write_disposition="append")
def fetch_mikrotik_logs():
    ROUTER_IP = os.getenv("ROUTER_IP", "192.168.88.1")
    url = f"https://{ROUTER_IP}/rest/log"
    response = requests.get(url, auth=(os.getenv("ROUTER_USER"), os.getenv("ROUTER_PASS")), verify=False)
    if response.status_code == 200:
        for log in response.json():
            yield log

def run_pipeline():
    pipeline = dlt.pipeline(pipeline_name="mikrotik_telemetry", destination="duckdb", dataset_name="network_diagnostics")
    load_info = pipeline.run(fetch_mikrotik_logs())
    print(load_info)

if __name__ == "__main__":
    run_pipeline()
