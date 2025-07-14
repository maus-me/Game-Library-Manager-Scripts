# Load modules
import time

from src.logger_config import setup_logging
from src.modules.config_parse import *
from src.modules.library_cleanup import post_library_cleanup
from src.modules.torrents import torrent_manager

# Configure logging before importing other modules
setup_logging()

import logging

logger = logging.getLogger(__name__)


def run():
    torrent_manager()
    post_library_cleanup()

def main():
    logging.basicConfig(filename='logs/logs.log', level=logging.INFO)
    logger.info("Starting the application...")

    if on_startup:
        logger.info("Running torrent manager on startup...")
        run()

    while True:
        logger.info(f"Waiting {wait_time} hours for the next cycle...")
        time.sleep(wait_time * 3600)
        run()


if __name__ == "__main__":
    main()
