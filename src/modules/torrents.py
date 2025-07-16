# Torrent handling module
import json
import logging
import os
import shutil

import qbittorrentapi

# Load modules
from src.modules.config_parse import *
from src.modules.helpers import fetch_json_data

logger = logging.getLogger(__name__)

API_RETRY_DELAY = 3600  # 1 hour

qbt_client = qbittorrentapi.Client(**conn_info)

def qbit_preflight():
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


def run():
    """
    Initial testing to see if we can retrieve torrents in a specific category that are done seeding.
    :return:
    """
    # Filter for torrents in the specific category that are done seeding.
    for torrent in qbt_client.torrents_info(category=QBIT_CATEGORY, limit=None, status_filter='completed'):
        # Validate the torrent state is "Stopped".  This means that the torrent has finished downloading AND seeding.
        if torrent.state == 'stoppedUP':
            # Log which torrents are in the category.  Includes the name, hash, and path.
            logger.info(f'Torrent: {torrent.name} | Hash: {torrent.hash} | Path: {torrent.content_path}')

            source = torrent.content_path
            name = torrent.name
            # Create new folder name based on the torrent name
            new_name = new_folder(name)

            # Copy and Delete to the game library root path
            destination = os.path.join(game_path, new_name)

            if move_torrent_folder(source, destination):
                delete_torrent(torrent.hash)


def move_torrent_folder(source, destination):
    """
    Move a torrent folder from source to destination.
    :param source: The source path of the torrent folder.
    :param destination: The destination path where the torrent folder should be moved.
    """
    if os.path.isdir(source):
        if os.path.exists(destination):
            try:
                logger.info(f'Deleting existing version: {destination}')
                shutil.rmtree(destination)
            except OSError as e:
                logger.error(f"Error deleting {destination}: {e}")
                return False
        try:
            shutil.move(source, destination)
            logger.info(f'Moved {source} to {destination}')
            return True
        except Exception as e:
            logger.error(f'Error moving {source}: {e}')
    return False


def delete_torrent(torrent_hash):
    """
    Delete a torrent from qBittorrent by its hash.
    :param torrent_hash: The hash of the torrent to delete.
    """
    try:
        qbt_client.torrents_delete(torrent_hashes=torrent_hash, delete_files=False)
        logger.info(f"Deleted torrent with hash: {torrent_hash}")
    except qbittorrentapi.APIConnectionError as e:
        logger.error(f"Failed to delete torrent with hash {torrent_hash}: {e}")

def new_folder(torrent_name):
    """
    Rework the folder name based on the torrent name.
    Example of original folder name: stalker_2_heart_of_chornobyl_windows_gog_(83415)

    :return: new folder name based on the torrent name.
    """
    new_name = torrent_name

    # Remove everything after the first underscore in _windows_gog_
    if '_windows_gog_' in new_name:
        new_name = torrent_name.split('_windows_gog_')[0]

    # Search cache/gog_recent_torrents.json for the torrent slug
    try:
        with open(GOG_ALL_GAMES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {GOG_ALL_GAMES_FILE}.")

        # Search the json for data["slug"] that matches the torrent_name
        for item in data:
            # if torrent_name equals the slug, set the torrent_name to the title of the item
            if new_name == item['slug']:
                new_name = item['title']
                logger.info(f'Found exact match: {item["slug"]} for title: {new_name}')
                break
            elif new_name in item['slug']:
                # If found, set the torrent_name to the title of the item
                new_name = item['title']
                logger.info(f'Found partial match: {item["slug"]} for title: {new_name}')
    except Exception as e:
        logger.error(f"Error loading {GOG_ALL_GAMES_FILE}. {e}")
        return None

    # Remove copyright characters and other unwanted characters that may appear in the metadata.
    for char in '©®™':
        new_name = new_name.replace(char, '')

    logger.info(f'Renamed folder: {torrent_name} to {new_name}')
    return new_name




def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")

    qbit_preflight()
    fetch_json_data(GOG_ALL_GAMES_URL, GOG_ALL_GAMES_FILE)
    run()
