# Torrent handling module
import logging
import os
import shutil
import subprocess

import qbittorrentapi

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
    :return:
    """
    new_name = torrent_name

    new_name = new_name.replace('_gog', f'{tag("GOG")}')
    new_name = new_name.replace('_windows', f'{tag("Windows")}')


    # Remove any remaining underscores (might not be needed?)
    new_name = new_name.replace('_', ' ')

    # Remove the 5 number wrapped in (), such as (78491) that is contained in the folder name
    new_name = ' '.join(
        word for word in new_name.split() if not (word.startswith('(') and word.endswith(')') and len(word) == 7))

    # Capitalize the first letter of each word except for words between ()
    new_name = ' '.join(
        word.capitalize() if not word.startswith('(') and not word.endswith(')') else word for word in
        new_name.split())

    # TODO: Add tweaks to handle the "Base" in folder names.
    # Examples of this would be: "Enhanced Edition Base" to "Enhanced Edition" or "Myst Base"
    # new_name = new_name.replace('Edition Base','Edition')

    logger.info(f'Renamed folder: {torrent_name} to {new_name}')
    return new_name


logger.info("Renaming completed.")

def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")

    auth_validation()
    test()
    # move_completed_torrents()


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
