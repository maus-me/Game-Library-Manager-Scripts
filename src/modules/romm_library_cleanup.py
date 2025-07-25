# ROMM Library Cleanup Module
import logging

from src.modules.api.romm import RommAPI
from src.modules.config_parse import *

logger = logging.getLogger(__name__)


def run():
    """
    Run the ROMM library cleanup process.
    This function will find and delete empty ROMMs.
    """
    if ROMM_ENABLE:
        logger.info("Starting ROMM library cleanup...")
        if ROMM_EMPTY_DIRS:
            find_empty()
        if ROMM_MISSING_EXE:
            find_missing_exe()
        if ROMM_SCAN_DANGEROUS_FILETYPES:
            find_dangerous_filetypes()
        logger.info("ROMM library cleanup completed.")
    else:
        logger.info("ROMM library cleanup is disabled in the configuration. Skipping...")


def find_empty():
    # Get the list of romms from the API
    logger.info("Removing empty directories...")
    romm_api = RommAPI()

    data = romm_api.filter_games(offset=0, order_by="fs_size_bytes", order_dir="asc", group_by_meta_id=True)
    game_ids = []

    for item in data.get('items', []):
        if item.get('fs_size_bytes') == 0:
            logger.info(f"Found empty ROMM: {item.get('name')} (ID: {item.get('id')})")
            # add the game ID to the list for deletion
            game_ids.append(item.get('id'))

    if game_ids:
        logger.info(f"Deleting empty ROMMs: {len(game_ids)} found.")
        romm_api.delete_games(game_ids)
    else:
        logger.info("No empty ROMMs found.")


def find_missing_exe():
    """
    Find ROMMs that are missing the executable file.
    This function will check each ROMM file for the presence of an executable file.
    """
    logger.info("Finding ROMMs with missing executables...")
    romm_api = RommAPI()

    data = romm_api.filter_games(offset=0, order_by="fs_size_bytes", order_dir="asc", group_by_meta_id=True)
    game_ids = []

    for item in data.get('items', []):
        is_exe_present = False

        for file in item.get('files', []):
            if file.get('file_name').endswith('.exe'):
                is_exe_present = True
                break

        if not is_exe_present:
            logger.info(f"Romm missing executable: {item.get('name')} (ID: {item.get('id')})")
            game_ids.append(item.get('id'))

    if game_ids:
        logger.info(f"Deleting ROMMs with missing executables: {len(game_ids)} found.")
        romm_api.delete_games(game_ids)
    else:
        logger.info("No ROMMs with missing executables found.")


def find_dangerous_filetypes():
    """
    Find ROMMs that contain dangerous file types.
    This function will check each ROMM file for the presence of dangerous file types.
    This is not an exhaustive list, but it includes common dangerous file types that should not exist with any legitimate game release like .bat and .cmd.
    It is recommended to add more file types as needed and to leverage a more comprehensive security solution like ClamAV.
    """
    logger.info("Finding ROMMs with dangerous file types...")
    romm_api = RommAPI()

    data = romm_api.filter_games(offset=0, order_by="fs_size_bytes", order_dir="asc", group_by_meta_id=True)
    game_ids = []

    for item in data.get('items', []):
        for file in item.get('files', []):
            if file.get('file_name').endswith(('.bat', '.cmd')):
                logger.warning(f"Romm has dangerous file: {item.get('name')} (ID: {item.get('id')})")
                game_ids.append(item.get('id'))
                break

    if game_ids:
        logger.info(f"ROMMs with dangerous files: {len(game_ids)} found.")
    else:
        logger.info("No ROMMs with dangerous files found.")
