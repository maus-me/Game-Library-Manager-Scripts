import base64
import logging

import requests

from src.modules.config_parse import ROMM_API_PASSWORD, ROMM_API_USERNAME, ROMM_API_URL, ROMM_PLATFORM_SLUG

logger = logging.getLogger(__name__)


class RommAPI:
    def __init__(self):
        self.session = requests.Session()
        self.username = ROMM_API_USERNAME
        self.password = ROMM_API_PASSWORD
        self.slug = ROMM_PLATFORM_SLUG
        self.url = ROMM_API_URL
        self.headers = {}

        # Shamelessly copied from muos-app
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            auth_token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            self.headers = {"Authorization": f"Basic {auth_token}"}

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.url}{endpoint}"
        try:
            # Ensure headers are included in each request
            if 'headers' in kwargs:
                kwargs['headers'].update(self.headers)
            else:
                kwargs['headers'] = self.headers

            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            if resp.content:
                return resp.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    # Delete Game Endpoint POST: /api/roms/delete
    # Json: {"roms":[{game_id}, {game_id}, {game_id}],"delete_from_fs":[]}
    def delete_games(self, game_ids):
        data = {"roms": game_ids, "delete_from_fs": []}
        logger.info(f"Deleting {len(game_ids)} empty ROMMs...")
        return self._request("POST", "/api/roms/delete", json=data)

    # Get Game Endpoint GET: /api/roms/{game_id}
    def get_game_by_id(self, game_id):
        return self._request("GET", f"/api/roms/{game_id}")

    def heartbeat(self):
        """
        Sends a heartbeat request to the ROMM API to keep the session alive.
        """
        return self._request("GET", "/api/heartbeat")

    def get_profile(self):
        """
        Retrieves the profile information of the authenticated user.
        """
        return self._request("GET", "/api/users/me")

    def get_config(self):
        """
        Retrieves the configuration settings from the ROMM API.
        """
        return self._request("GET", "/api/config")

    # Get Platforms Endpoint GET: /api/platforms
    def get_platforms(self):
        """
        Retrieves the list of platforms from the ROMM API.
        :return: A list of platforms in json.
        """
        return self._request("GET", "/api/platforms")

    def get_collections(self):
        """
        Retrieves the manually created collections from the ROMM API.
        """

        return self._request("GET", "/api/collections")

    def get_virtual_collections(self):
        """
        Retrieves the virtual collections from the ROMM API.
        """
        return self._request("GET", "/api/collections/virtual?type=collection")

    def get_platform_by_slug(self):
        """
        Retrieves a platform by its slug.
        :return: The platform id if found, otherwise None.
        """
        platforms = self.get_platforms()
        if platforms:
            for platform in platforms:
                if platform.get('fs_slug') == self.slug:
                    return platform.get('id')
        return None

    def filter_games(self, platform_id=None, limit=None, **kwargs):
        """
        Filters games based on various parameters.
        :param platform_id: The ID of the platform to filter by.
        :param limit: The maximum number of games to return.
        :param offset: The offset for pagination.
        :param order_by: The field to order the results by.
        :param order_dir: The direction of the ordering (asc or desc).
        :param group_by_meta_id: Whether to group by meta ID.
        :return: A list of filtered games.
        """

        params = {
            # "platform_id": platform_id,
            # "limit": limit,
            # "offset": offset,
            # "order_by": order_by,
            # "order_dir": order_dir,
            # "group_by_meta_id": str(group_by_meta_id).lower()
        }
        if platform_id is not None:
            params['platform_id'] = platform_id

        if limit is not None:
            params['limit'] = limit

        params.update(kwargs)

        return self._request("GET", "/api/roms", params=params)

    @staticmethod
    def test():
        heartbeat = RommAPI().heartbeat()
        # print(f"Heartbeat response: {heartbeat}")

        get_game_by_id = RommAPI().get_game_by_id(38567)
        # print(f"Get game by ID response: {get_game_by_id}")

        get_profile = RommAPI().get_profile()
        # print(f"Get profile response: {get_profile}")

        get_config = RommAPI().get_config()
        # print(f"Get config response: {get_config}")

        # get_platforms = RommAPI().get_platforms()
        # print(f"Get platforms response: {get_platforms}")

        get_collections = RommAPI().get_collections()
        # print(f"Get collections response: {get_collections}")

        get_virtual_collections = RommAPI().get_virtual_collections()
        # print(f"Get virtual collections response: {get_virtual_collections}")

        get_platform_by_slug = RommAPI().get_platform_by_slug()
        # print(f"Get platform by slug response: {get_platform_by_slug}")

        # delete_games = RommAPI().delete_games([34691])

        filter_games = RommAPI().filter_games()
        # print(f"Filter games response: {pprint.pprint(filter_games)}")
