# Game library cleanup module


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
    remove_empty()

    logger.info("Post-library cleanup completed.")


def remove_extras():
    """
    Delete the .zip files that are not needed such as,
    _soundtrack_, OST, FLAC, WAV, MP3, etc.
    :return:
    """
    logger.info("Removing unnecessary files...")

    zip_strings = ['soundtrack', '_ost', 'flac', '_wav', 'mp3', 'artbook']

    for folder in os.listdir(game_path):
        folder_path = os.path.join(game_path, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                # calculate filesize
                size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0

                # Text file cleanup
                if file.endswith('gog-games.to.txt'):
                    try:
                        os.remove(file_path)
                        logger.info(f'Removed txt: {trim_path(file_path)} | Size: {format_size(size)}')
                    except Exception as e:
                        logger.error(f'Error removing file {file_path}: {e}')


                # Zip file cleanup
                if any(zip_string.lower() in file.lower() for zip_string in zip_strings) and file.endswith('.zip'):
                    try:
                        # os.remove(file_path)
                        # log which file was removed and the size of the file
                        logger.info(f'Removed extras: {trim_path(file_path)} | Size: {format_size(size)}')
                    except Exception as e:
                        logger.error(f'Error removing file {file_path}: {e}')

    logger.info("Removal of unnecessary files completed.")

def remove_empty():
    """
    Remove empty directories in the game library root path.
    :return:
    """
    logger.info("Removing empty directories...")

    for folder in os.listdir(game_path):
        folder_path = os.path.join(game_path, folder)
        if os.path.isdir(folder_path):
            # Check if the directory is empty
            if not os.listdir(folder_path):
                try:
                    os.rmdir(folder_path)
                    logger.info(f'Removed empty directory: {folder_path}')
                except OSError as e:
                    logger.error(f'Error removing empty directory {folder_path}: {e}')

    logger.info("Empty directory removal completed.")


def trim_path(path):
    """
    Trim the path to only the last part of the path and parent directory.
    :param path: The path to trim.
    :return: The trimmed path.
    """
    if not path:
        return ""
    # Split the path into parts
    parts = path.split(os.sep)
    # Return the last part and the parent directory
    # TODO: Review this code, it might not work as expected in all cases
    return os.path.join(parts[-2], parts[-1]) if len(parts) > 1 else parts[-1]


def format_size(size, suffix="B"):
    """
    Format the size in a human-readable format.
    :param size: The size in bytes.
    :return:
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(size) < 1024.0:
            return f"{size:3.1f}{unit}{suffix}"
        size /= 1024.0
    return f"{size:.1f}Yi{suffix}"
