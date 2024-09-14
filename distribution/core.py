import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def version():
    try:
        response = requests.get("https://raw.githubusercontent.com/ftnick/feature/main/host/version.txt")
        response.raise_for_status()
        version = response.text.strip()
        return version
    except requests.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.ConnectionError as conn_err:
        logging.error(f"Connection error occurred: {conn_err}")
    except requests.Timeout as timeout_err:
        logging.error(f"Timeout error occurred: {timeout_err}")
    except requests.RequestException as req_err:
        logging.error(f"Error occurred: {req_err}")
    return None