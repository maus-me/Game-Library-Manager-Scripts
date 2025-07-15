# Misc Helper Functions
import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"


def fetch_json_data(url, filename):
    """
    Fetch data from the given URL and save it to the specified file.
    :param url: API endpoint to fetch data from.
    :param filename: File path to save the fetched data.
    """
    try:
        response = requests.get(url)

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if response.status_code == 200:
            data = response.json()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved data to {filename}")
        else:
            logger.error(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
