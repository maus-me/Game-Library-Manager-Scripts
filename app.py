# Load modules
import logging
import time

from src.logger_config import setup_logging
from src.modules.config_parse import LOG_FILE_PATH, ON_STARTUP, WAIT_TIME
from src.modules.library_cleanup import post_library_cleanup
from src.modules.torrents import torrent_manager

# Configure logging before importing other modules
setup_logging(log_file_path=LOG_FILE_PATH)
logger = logging.getLogger(__name__)


def run():
    torrent_manager()
    post_library_cleanup()

def main():
    """Main application loop that runs on schedule."""
    logger.info("Starting the application...")

    if ON_STARTUP:
        logger.info("Running torrent manager on startup...")
        run()

    while True:
        wait_seconds = WAIT_TIME * 3600
        logger.info(f"Waiting {WAIT_TIME} hours for the next cycle...")
        time.sleep(wait_seconds)
        run()


if __name__ == "__main__":
    main()
