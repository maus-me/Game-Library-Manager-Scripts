# Torrent handling module
import json
import logging
import os
import shutil
import subprocess

import qbittorrentapi
import requests

# Load modules
from src.modules.config_parse import *

logger = logging.getLogger(__name__)

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
            destination = os.path.join(game_path, new_name)

            if os.path.isdir(source):
                # Check if the destination directory already exists and delete it if it does
                if os.path.exists(destination):
                    try:
                        logger.info(f'Deleting existing version: {destination}')
                        shutil.rmtree(destination)
                    except OSError as e:
                        logger.error("Error: %s - %s." % (e.filename, e.strerror))
                # Move the torrent folder to the game library root path
                try:
                    subprocess.run(['mv', source, destination], check=True)
                    logger.info(f'Moved {source} to {destination}')
                except subprocess.CalledProcessError as e:
                    logger.error(f'Error moving {source}: {e}')

            # Delete the torrent from qBittorrent
            qbt_client.torrents_delete(torrent_hashes=torrent.hash, delete_files=False)


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
        with open('cache/gog_all_games.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info("Loaded gog_all_games.json.")

        # Search the json for data["slug"] that matches the torrent_name
        for item in data:
            # if torrent_name equals the slug, set the torrent_name to the title of the item
            if torrent_name in item['slug']:
                # If found, set the torrent_name to the title of the item
                new_name = item['title']
                logger.info(f'Found matching slug: {item["slug"]} for title: {torrent_name}')
    except:
        logger.error("Error loading gog_all_games.json. Make sure the file exists and is valid JSON.")
        return None

    logger.info(f'Renamed folder: {torrent_name} to {new_name}')
    return new_name


def get_gog_recent_torrents():
    """
    Save the json data from the GOG API to a file.=.
    https://gog-games.to/api/web/recent-torrents
    """

    url = "https://gog-games.to/api/web/recent-torrents"
    response = requests.get(url)

    # Ensure the cache directory exists
    filename = 'cache/gog_recent_torrents.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if response.status_code == 200:
        data = response.json()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info("Saved recent torrents data to gog_recent_torrents.json")


def get_gog_all_games():
    """
    Save the json data from the GOG API to a file.
    https://gog-games.to/api/web/all-games
    """
    url = "https://gog-games.to/api/web/all-games"
    response = requests.get(url)

    # Ensure the cache directory exists
    filename = 'cache/gog_all_games.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    if response.status_code == 200:
        data = response.json()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info("Saved all games data to gog_all_games.json")




def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")

    auth_validation()
    # get_gog_recent_torrents()
    get_gog_all_games()
    test()

    # move_completed_torrents()


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
