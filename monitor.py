"""Module for monitoring endpoints when provided a YAML file."""

import time
from collections import defaultdict
import logging

import requests
import yaml
import tldextract
from schema import Schema, Optional, SchemaError

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs/endpoint_monitor.log",
    format="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def load_config(file_path):
    """
    Function to load configuration from the YAML file.
    """
    logger.info("Load config file.")
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

def check_schema(config):
    """
    Validate the YAML file has all required fields.
    """
    logger.info("Validating YAML schema.")
    config_schema = Schema(
        [
            {
                "name": str,
                "url": str,
                Optional("method"): str,
                Optional("headers"): dict,
                Optional("body"): str
            }
        ]
    )
    try:
        config_schema.validate(config)
    except SchemaError as err:
        logger.error(f"SchemaError:{err}")

def check_health(endpoint):
    """
    Function to perform health checks.
    """

    url = endpoint["url"]

    method = "GET" if endpoint.get("method") is None else endpoint.get("method")
    headers = endpoint.get("headers")

    body = endpoint.get("body")

    try:
        response = requests.request(
            method, url, headers=headers, json=body, timeout=0.5
        )

        if 200 <= response.status_code < 300:
            return "UP"

        else:
            return "DOWN"

    except requests.RequestException:
        return "DOWN"


def extract_domain(url):
    """
    Extracts domain from url, ignoring port
    """

    extraction = tldextract.extract(url)

    domain = extraction.registered_domain

    return domain


def monitor_endpoints(file_path):
    """
    Main function to monitor endpoints.
    """
    config = load_config(file_path)
    check_schema(config)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    while True:
        for endpoint in config:
            domain = extract_domain(endpoint["url"])

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
        logger.error("Usage: python monitor.py <config_file_path>")

        print("Usage: python monitor.py <config_file_path>")

        sys.exit(1)

    config_file = sys.argv[1]

    try:
        logger.info("Starting endpoint monitor.")
        monitor_endpoints(config_file)

    except KeyboardInterrupt:
        logger.error("KeyboardInterrupt: Monitoring stopped by user.")

        print("\nMonitoring stopped by user.")
