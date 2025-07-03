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
            new_name = folder

            new_name = new_name.replace('_gog', f'{tag("GOG")}')
            new_name = new_name.replace('_windows', f'{tag("Windows")}')

            # Remove any remaining underscores (might not be needed?)
            new_name = new_name.replace('_', ' ')

            # Capitalize the first letter of each word except for words between ()
            new_name = ' '.join(
                word.capitalize() if not word.startswith('(') and not word.endswith(')') else word for word in
                new_name.split())


            os.rename(os.path.join(game_path, folder), os.path.join(game_path, new_name))
            logger.info(f'Renamed folder: {folder} to {new_name}')

    logger.info("Renaming completed.")


def tag(value):
    """
    Function to apply tag to folder name consistently based on value passed to function.
    """
    if value:
        return f" ({value})"

# Search through folders for .txt files and remove them
def cleanup_folders():
    logger.info("Starting to clean up folders...")
    for folder in os.listdir(game_path):
        folder_path = os.path.join(game_path, folder)
        if os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.endswith('gog-games.to.txt'):
                    file_path = os.path.join(folder_path, file)
                    os.remove(file_path)
                    logger.info(f'Removed file: {file} from folder: {folder}')

    logger.info("Cleanup completed.")


# Main function to execute the renaming
def main():
    logging.basicConfig(filename='logs/logs.log', level=logging.INFO)

    rename_folders()
    cleanup_folders()


if __name__ == "__main__":
    main()
