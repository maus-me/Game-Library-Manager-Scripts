# Torrent handling module
#
# Problem 1:
# Moving the files may fail/corrupt if torrent is still seeding.
# This can be mitigated by checking if the torrent is still seeding before moving it, and then stopping the seed or returning at a later run?
# Problem 2:
# Lingering torrents will cause a new directory to be created with the same name.
# Move completed torrents to the game library root path
import logging
import os
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
            rename_folder(name)

            # Delete the torrent from qBittorrent
            # TODO: Uncomment the line below to enable deletion of torrents
            # qbt_client.torrents_delete(torrent_hashes=torrent.hash, delete_files=False)

            # Copy and Delete to the game library root path
            # destination = os.path.join(game_path, f'{}')


def rename_folder(torrent_name):
    """
    Rename the folder based on the torrent name.
    :return:
    """
    # This function is not currently used, but can be used to rename folders based on the torrent name.
    new_name = torrent_name

    new_name = new_name.replace('_gog', f'{tag("GOG")}')
    new_name = new_name.replace('_windows', f'{tag("Windows")}')

    # Remove any remaining underscores (might not be needed?)
    new_name = new_name.replace('_', ' ')

    # Capitalize the first letter of each word except for words between ()
    new_name = ' '.join(
        word.capitalize() if not word.startswith('(') and not word.endswith(')') else word for word in
        new_name.split())

    # os.rename(os.path.join(torrent_path, torrent_name), os.path.join(torrent_path, new_name))
    logger.info(f'Renamed folder: {torrent_name} to {new_name}')


logger.info("Renaming completed.")

def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")

    auth_validation()
    test()
    # rename_folders()
    # move_completed_torrents()
    logger.info("Torrent management completed.")


def move_completed_torrents():
    logger.info("Starting to move completed torrents...")
    for folder in os.listdir(torrent_path):
        source = os.path.join(torrent_path, folder)
        if os.path.isdir(source):
            # Move the torrent file to the game library root path
            destination = os.path.join(game_path, folder)
            try:
                subprocess.run(['mv', source, destination], check=True)
                logger.info(f'Moved {source} to {destination}')
            except subprocess.CalledProcessError as e:
                logger.error(f'Error moving {source}: {e}')

    logger.info("Completed moving torrents.")


# For each folder in the current directory remove the part of the foldername
# def rename_folders():
#     logger.info("Starting to rename folders...")
#     for folder in os.listdir(torrent_path):
#         if os.path.isdir(os.path.join(torrent_path, folder)):
#             # Do the renaming
#             new_name = folder
#
#             new_name = new_name.replace('_gog', f'{tag("GOG")}')
#             new_name = new_name.replace('_windows', f'{tag("Windows")}')
#
#             # Remove any remaining underscores (might not be needed?)
#             new_name = new_name.replace('_', ' ')
#
#             # Capitalize the first letter of each word except for words between ()
#             new_name = ' '.join(
#                 word.capitalize() if not word.startswith('(') and not word.endswith(')') else word for word in
#                 new_name.split())
#
#             os.rename(os.path.join(torrent_path, folder), os.path.join(torrent_path, new_name))
#             logger.info(f'Renamed folder: {folder} to {new_name}')
#
#     logger.info("Renaming completed.")


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
