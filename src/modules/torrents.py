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

# Load modules
from src.modules.config_parse import *

logger = logging.getLogger(__name__)


def torrent_manager():
    """
    Manage torrents by renaming folders and moving completed torrents to the game library root path.
    :return:
    """
    logger.info("Starting torrent manager...")
    rename_folders()
    move_completed_torrents()
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
def rename_folders():
    logger.info("Starting to rename folders...")
    for folder in os.listdir(torrent_path):
        if os.path.isdir(os.path.join(torrent_path, folder)):
            # Do the renaming
            new_name = folder

            new_name = new_name.replace('_gog', f'{tag("GOG")}')
            new_name = new_name.replace('_windows', f'{tag("Windows")}')

            # Remove any remaining underscores (might not be needed?)
            new_name = new_name.replace('_', ' ')

            # Capitalize the first letter of each word except for words between ()
            new_name = ' '.join(
                word.capitalize() if not word.startswith('(') and not word.endswith(')') else word for word in
                new_name.split())

            os.rename(os.path.join(torrent_path, folder), os.path.join(torrent_path, new_name))
            logger.info(f'Renamed folder: {folder} to {new_name}')

    logger.info("Renaming completed.")


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"
