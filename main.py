"""Module for monitoring endpoints when provided a YAML file."""
import time
from collections import defaultdict

import requests
import yaml



def load_config(file_path):
    """
    Function to load configuration from the YAML file.
    """
    with open(file_path, "r", encoding='utf-8') as file:
        return yaml.safe_load(file)



def check_health(endpoint):
    """
    Function to perform health checks.
    """
    url = endpoint["url"]
    method = "GET" if endpoint.get("method") is None else endpoint.get("method")
    headers = endpoint.get("headers")
    body = endpoint.get("body")

    try:
        response = requests.request(method, url, headers=headers, json=body, timeout=.5)
        if 200 <= response.status_code < 300:
            return "UP"
        else:
            return "DOWN"
    except requests.RequestException:
        return "DOWN"



def monitor_endpoints(file_path):
    """
    Main function to monitor endpoints.
    """
    config = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        for endpoint in config:
            domain = endpoint["url"].split("//")[-1].split("/")[0]
            result = check_health(endpoint)

            domain_stats[domain]["total"] += 1
            if result == "UP":
                domain_stats[domain]["up"] += 1

        # Log cumulative availability percentages
        for domain, stats in domain_stats.items():
            availability = round(100 * stats["up"] / stats["total"])
            print(f"{domain} has {availability}% availability percentage")

        print("---")
        time.sleep(15)


# Entry point of the program
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python monitor.py <config_file_path>")
        sys.exit(1)

    config_file = sys.argv[1]
    try:
        monitor_endpoints(config_file)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
