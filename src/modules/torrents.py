# Torrent handling module
import json
import logging
import os
import shutil
import subprocess
import time

import qbittorrentapi
import requests

# Load modules
from src.modules.config_parse import *

logger = logging.getLogger(__name__)

CACHE_DIR = 'cache'
GOG_ALL_GAMES_FILE = os.path.join(CACHE_DIR, 'gog_all_games.json')
GOG_RECENT_TORRENTS_FILE = os.path.join(CACHE_DIR, 'gog_recent_torrents.json')
API_RETRY_DELAY = 3600  # 1 hour


qbt_client = qbittorrentapi.Client(**conn_info)


def auth_validation():
    """
    Test Authentication with qBittorrent and log the app version and web API version.
    :return:
    """
    try:
        qbt_client.auth_log_in()

        logger.info(f"qBittorrent App Version: {qbt_client.app.version}")
        logger.info(f"qBittorrent Web API: {qbt_client.app.web_api_version}")

    except qbittorrentapi.LoginFailed as e:
        logger.error(f"qBittorrent Login failed: {e}")
        exit(1)


def test():
    """
    Initial testing to see if we can retrieve torrents in a specific category that are done seeding.
    :return:
    """
    # Filter for torrents in the specific category that are done seeding.
    for torrent in qbt_client.torrents_info(category=qbit_category, limit=None, status_filter='completed'):
        # Validate the torrent state is "Stopped".  This means that the torrent has finished downloading AND seeding.
        if torrent.state == 'stoppedUP':
            # Log which torrents are in the category.  Includes the name, hash, and path.
            logger.info(f'Torrent: {torrent.name} | Hash: {torrent.hash} | Path: {torrent.content_path}')

            source = torrent.content_path
            name = torrent.name
            # Create new folder name based on the torrent name
            new_name = new_folder(name)

            # Copy and Delete to the game library root path
            destination = str(os.path.join(game_path, new_name))

            move_folder(source, destination)

            # Delete the torrent from qBittorrent
            qbt_client.torrents_delete(torrent_hashes=torrent.hash, delete_files=False)


def move_folder(source: str, destination: str):
    """
    Move a folder from source to destination.
    :param source: Source folder path
    :param destination: Destination folder path
    :return:
    """
    if not os.path.isdir(source):
        logger.error(f"Source path does not exist or is not a directory: {source}")
        return
    if os.path.exists(destination):
        try:
            logger.info(f"Deleting existing destination: {destination}")
            shutil.rmtree(destination)
        except OSError as e:
            logger.error(f"Error deleting {destination}: {e}")
            return

    try:
        # Move the folder to the destination using subprocess
        subprocess.run(['mv', source, destination], check=True)
        logger.info(f'Moved {source} to {destination}')
    except Exception as e:
        logger.error(f'Error moving {source} to {destination}: {e}')
        exit(1)


def new_folder(torrent_name):
    """
    Rework the folder name based on the torrent name.
    Example of original folder name: stalker_2_heart_of_chornobyl_windows_gog_(83415)

    :return:
    """
    new_name = torrent_name

    # Remove everything after the first underscore in _windows_gog_
    if '_windows_gog_' in new_name:
        new_name = torrent_name.split('_windows_gog_')[0]

    # Search cache/gog_recent_torrents.json for the torrent slug
    try:
        with open(GOG_ALL_GAMES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            if torrent_name == item['slug']:
                new_name = item['title']
                logger.info(f'Found an exact match: {item["slug"]} for title: {torrent_name}')
                break
            elif torrent_name in item['slug']:
                new_name = item['title']
                logger.info(f'Found a partial match: {item["slug"]} for title: {torrent_name}')
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading {GOG_ALL_GAMES_FILE}. {e}")
        return None

    # Remove copyright characters and other unwanted characters that may appear in the metadata.
    chars = ['©', '®', '™']
    for char in chars:
        new_name = new_name.replace(char, '')


    logger.info(f'Renamed folder: {torrent_name} to {new_name}')
    return new_name


def fetch_api_data(url: str, filename: str, retries: int = 3):
    """
    Fetch and save to file.
    We want to be respectful of the service,
    so we will cache the data.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    for attempt in range(retries):
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                logger.info(f"Saved data to {filename}")
                return data
        except requests.RequestException as e:
            logger.error(f"API error on attempt: {e}")
            if attempt < retries - 1:
                time.sleep(API_RETRY_DELAY)
    logger.error(f"Failed to fetch data from {url} after {retries} attempts.")
    return None


def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")

    auth_validation()

    fetch_api_data("https://gog-games.to/api/web/all-games", GOG_ALL_GAMES_FILE)
    test()

    # move_completed_torrents()


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
