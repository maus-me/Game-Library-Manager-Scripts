# Load modules
from src.logger_config import setup_logging
from src.modules.library_cleanup import post_library_cleanup

# Configure logging before importing other modules
setup_logging()

import logging

logger = logging.getLogger(__name__)


# Main function to execute the renaming
def main():
    logging.basicConfig(filename='logs/logs.log', level=logging.INFO)
    logger.info("Starting the application...")

    torrent_manager()
    post_library_cleanup()


if __name__ == "__main__":
    main()
