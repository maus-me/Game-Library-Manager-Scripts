"""
Configuration Parser Module

This module handles loading and parsing of configuration settings from config files.
It provides access to configuration values through exported variables and functions.
"""

import configparser
import logging
import os
from typing import Any, List

# Set up logger
logger = logging.getLogger(__name__)


def create_config_parser() -> configparser.ConfigParser:
    """
    Create and initialize a ConfigParser object with appropriate settings.
    
    Returns:
        configparser.ConfigParser: Initialized ConfigParser object
    """
    parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    parser.optionxform = str.lower
    return parser


def load_config(config_paths: List[str] = None) -> configparser.ConfigParser:
    """
    Load configuration from specified paths or default paths.

    Args:
        config_paths: List of configuration file paths to try (in order of preference)

    Returns:
        configparser.ConfigParser: ConfigParser object with loaded configuration
    """
    if config_paths is None:
        config_paths = ["config_hidden.cfg", "config.cfg"]

    config_parser = create_config_parser()

    # Try to read from each path in the list
    for path in config_paths:
        if os.path.exists(path):
            try:
                config_parser.read(path, encoding="utf-8")
                logger.info(f"Loaded configuration from {path}")
                return config_parser
            except Exception as e:
                logger.error(f"Error loading configuration from {path}: {e}")

    return config_parser


def get_config_value(config_parser: configparser.ConfigParser, section: str, option: str,
                     default: Any = None, value_type: str = "str") -> Any:
    """
    Get a configuration value with error handling and type conversion.
    
    Args:
        config_parser: ConfigParser object to get value from
        section: Configuration section name
        option: Configuration option name
        default: Default value to return if option is not found
        value_type: Type of value to return ('str', 'int', 'float', 'bool', 'list')
        
    Returns:
        Configuration value with appropriate type
    """
    try:
        if value_type == "str":
            return config_parser.get(section, option)
        elif value_type == "int":
            return config_parser.getint(section, option)
        elif value_type == "float":
            return config_parser.getfloat(section, option)
        elif value_type == "bool":
            return config_parser.getboolean(section, option)
        elif value_type == "list":
            value = config_parser.get(section, option)
            return [item.strip() for item in value.split(",") if item.strip()]
        else:
            logger.warning(f"Unknown value type '{value_type}' for {section}.{option}. Using string.")
            return config_parser.get(section, option)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logger.warning(f"Configuration {section}.{option} not found: {e}. Using default value: {default}")
        return default
    except Exception as e:
        logger.error(f"Error getting configuration {section}.{option}: {e}. Using default value: {default}")
        return default


# Load configuration
config_parser = load_config()

# Admin section
game_path = get_config_value(config_parser, "admin", "game_library_root_path", "/data/library/")
torrent_path = get_config_value(config_parser, "admin", "torrents_completed_root_path", "/data/torrent/")
LOG_FILE_PATH = get_config_value(config_parser, "admin", "log_file_path", "logs/logs.log")
WAIT_TIME = get_config_value(config_parser, "admin", "wait_time_hours", 4, "int")
ON_STARTUP = get_config_value(config_parser, "admin", "on_startup", True, "bool")
DEBUG_LOGGING = get_config_value(config_parser, "admin", "debug_logging", False, "bool")

# qBittorrent section
conn_info = {
    "host": get_config_value(config_parser, "qbittorrent", "host", "localhost"),
    "port": get_config_value(config_parser, "qbittorrent", "port", 8080, "int"),
    "username": get_config_value(config_parser, "qbittorrent", "username", "admin"),
    "password": get_config_value(config_parser, "qbittorrent", "password", "password"),
}
QBIT_CATEGORY = get_config_value(config_parser, "qbittorrent", "category", "gog")
MAX_TORRENTS_PER_RUN = get_config_value(config_parser, "qbittorrent", "max_torrents_per_run", 0, "int")
DELETE_AFTER_PROCESSING = get_config_value(config_parser, "qbittorrent", "delete_after_processing", True, "bool")

# GOG section
GOG_ALL_GAMES_FILE = get_config_value(config_parser, "gog", "gog_all_games_file", "cache/gog_all_games.json")
GOG_RECENT_GAMES_FILE = get_config_value(config_parser, "gog", "gog_recent_games_file", "cache/gog_recent_games.json")
GOG_ALL_GAMES_URL = get_config_value(config_parser, "gog", "gog_all_games_url",
                                     "https://gog-games.to/api/web/all-games")
GOG_RECENT_GAMES_URL = get_config_value(config_parser, "gog", "gog_recent_games_url",
                                        "https://gog-games.to/api/web/recent-torrents")
CACHE_REFRESH_HOURS = get_config_value(config_parser, "gog", "cache_refresh_hours", 24, "int")

# Cleanup section
REMOVE_EXTRAS = get_config_value(config_parser, "cleanup", "remove_extras", True, "bool")
EXTRAS_PATTERNS = get_config_value(config_parser, "cleanup", "extras_patterns",
                                   "soundtrack,ost,flac,wav,mp3,artbook,booklet,wallpaper", "list")
REMOVE_EMPTY_DIRS = get_config_value(config_parser, "cleanup", "remove_empty_dirs", True, "bool")
REMOVE_TEXT_FILES = get_config_value(config_parser, "cleanup", "remove_text_files", True, "bool")

# Export all variables and functions that should be available when importing this module
__all__ = [
    # Admin section
    "game_path",
    "torrent_path",
    "LOG_FILE_PATH",
    "WAIT_TIME",
    "ON_STARTUP",
    "DEBUG_LOGGING",

    # qBittorrent section
    "conn_info",
    "QBIT_CATEGORY",
    "MAX_TORRENTS_PER_RUN",
    "DELETE_AFTER_PROCESSING",

    # GOG section
    "GOG_ALL_GAMES_FILE",
    "GOG_RECENT_GAMES_FILE",
    "GOG_ALL_GAMES_URL",
    "GOG_RECENT_GAMES_URL",
    "CACHE_REFRESH_HOURS",

    # Cleanup section
    "REMOVE_EXTRAS",
    "EXTRAS_PATTERNS",
    "REMOVE_EMPTY_DIRS",
    "REMOVE_TEXT_FILES"
]