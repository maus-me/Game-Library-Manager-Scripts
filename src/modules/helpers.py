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
    return f" ({value})" if value else None

def fetch_json_data(url, filename):
    """
    Fetch data from the given URL and save it to the specified file.
    :param url: API endpoint to fetch data from.
    :param filename: File path to save the fetched data.
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()  # Raise exception for non-200 status codes

        # Create directory structure if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Save data to file
        data = response.json()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f"Saved data to {filename}")
        return True

    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return False
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error processing data from {url}: {e}")
        return False


def format_size(size, suffix="B"):
    """
    Format the size in a human-readable format.
    :param suffix: The suffix to append to the size (default is "B" for bytes).
    :param size: The size in bytes.
    :return:
    """
    units = ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi")

    for unit in units:
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}{suffix}"
        size /= 1024.0

    return f"{size:.1f}Yi{suffix}"