import configparser

config_parser = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config_parser.optionxform = str.lower

# Check if config_hidden.cfg exists, if so, use that, otherwise use config.cfg
if not config_parser.read("config_hidden.cfg", encoding="utf-8"):
    config_parser.read("config.cfg")

# Set global variables for the game path and torrent path
game_path = config_parser.get("admin", "game_library_root_path")
torrent_path = config_parser.get("admin", "torrents_completed_root_path")

# Qbittorrent connection information
conn_info = {
    "host": config_parser.get("qbittorrent", "host"),
    "port": config_parser.getint("qbittorrent", "port"),
    "username": config_parser.get("qbittorrent", "username"),
    "password": config_parser.get("qbittorrent", "password"),
}
qbit_category = config_parser.get("qbittorrent", "category")

__all__ = [
    "game_path",
    "torrent_path",
    "conn_info",
    "qbit_category"
]
