import requests

def version():
    try:
        response = requests.get("nort")
        response.raise_for_status()
        version = response.text.strip()
        return version
    except requests.RequestException as e:
        print(f"Error fetching version: {e}")
        return None
