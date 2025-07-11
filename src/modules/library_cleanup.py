# Cleanup the library by renaming folders and removing unnecessary files

import logging
import os

# Load modules
from src.modules.config_parse import *

logger = logging.getLogger(__name__)


def post_library_cleanup():
    """
    Perform post-library cleanup tasks such as renaming folders and removing unnecessary files.
    :return:
    """
    logger.info("Post-library cleanup...")

    # Remove unnecessary files
    remove_extras()

    logger.info("Post-library cleanup completed.")


def remove_extras():
    """
    Delete the .zip files that are not needed such as,
    _soundtrack_, OST, FLAC, WAV, MP3, etc.
    :return:
    """
    logger.info("Removing unnecessary files...")

    zip_strings = ['_soundtrack_', 'OST', 'FLAC', 'WAV', 'MP3']

    for folder in os.listdir(game_path):
        folder_path = os.path.join(game_path, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if any(zip_string in file for zip_string in zip_strings) and file.endswith('.zip'):
                    zip_file = os.path.join(folder_path, file)
                    try:
                        # os.remove(zip_path)
                        logger.info(f'Removed unnecessary file: {zip_file}')
                    except Exception as e:
                        logger.error(f'Error removing file {zip_file}: {e}')

    logger.info("Removal of unnecessary files completed.")
