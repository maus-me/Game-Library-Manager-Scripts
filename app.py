# At the beginning of app.py


from src.logger_config import setup_logging

# Configure logging before importing other modules
setup_logging()

import os
import logging
import configparser

logger = logging.getLogger(__name__)

config_parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config_parser.optionxform = str.lower

# Check if config_hidden.cfg exists, if so, use that, otherwise use config.cfg
if config_parser.read("config_hidden.cfg", encoding="utf-8") == []:
    config_parser.read("config.cfg")

# Variable for the game path
game_path = config_parser.get("admin", "game_library_root_path")


# For each folder in the current directory remove the part of the foldername
def rename_folders():
    logger.info("Starting to rename folders...")
    for folder in os.listdir(game_path):
        if os.path.isdir(os.path.join(game_path, folder)):
            # Do the renaming
            new_name = folder.replace('_windows_gog_', '')
            # Remove any remaining underscores
            new_name = new_name.replace('_', ' ')

            os.rename(os.path.join(game_path, folder), os.path.join(game_path, new_name))
            logger.info(f'Renamed folder: {folder} to {new_name}')

    logger.info("Renaming completed.")


# Main function to execute the renaming
def main():
    logging.basicConfig(filename='logs/logs.log', level=logging.INFO)

    rename_folders()


if __name__ == "__main__":
    main()
