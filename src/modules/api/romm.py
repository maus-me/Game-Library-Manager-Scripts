import base64
import logging
from typing import Dict, List, Optional

import requests

from src.modules.config_parse import ROMM_API_PASSWORD, ROMM_API_USERNAME, ROMM_API_URL, ROMM_PLATFORM_SLUG

logger = logging.getLogger(__name__)


class RommAPI:
    def __init__(self):
        self.session = requests.Session()
        self.username = ROMM_API_USERNAME
        self.password = ROMM_API_PASSWORD
        self.slug = ROMM_PLATFORM_SLUG
        self.base_url = ROMM_API_URL
        self.headers = self._create_auth_headers()

    def _create_auth_headers(self) -> Dict[str, str]:
        """Create authentication headers using Basic Auth."""
        if self.username and self.password:
            credentials = f"{self.username}:{self.password}"
            auth_token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            return {"Authorization": f"Basic {auth_token}"}
        return {}

    def _request(self, method, endpoint, **kwargs):
        """
        Send a request to the ROMM API.

        Args:
            method: HTTP method to use
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests.request

        Returns:
            JSON response data or None if no content

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
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

    def delete_games(self, game_ids: List[int]) -> Optional[Dict]:
        """
        Delete games from ROMM.

        Args:
            game_ids: List of game IDs to delete

        Returns:
            API response
        """
        data = {"roms": game_ids, "delete_from_fs": []}
        logger.info(f"Deleting {len(game_ids)} empty ROMMs...")
        return self._request("POST", "/api/roms/delete", json=data)

    # Get Game Endpoint GET: /api/roms/{game_id}
    def get_game_by_id(self, game_id: int) -> Optional[Dict]:
        """
        Retrieve game details by ID.

        Args:
            game_id: ID of the game to retrieve

        Returns:
            Game details
        """
        return self._request("GET", f"/api/roms/{game_id}")

    def heartbeat(self) -> Optional[Dict]:
        """
        Send a heartbeat request to keep the session alive.

        Returns:
            Heartbeat response
        """
        return self._request("GET", "/api/heartbeat")

    def get_profile(self) -> Optional[Dict]:
        """
        Retrieve authenticated user profile information.

        Returns:
            User profile data
        """
        return self._request("GET", "/api/users/me")

    def get_config(self) -> Optional[Dict]:
        """
        Retrieve ROMM configuration settings.

        Returns:
            Configuration settings
        """
        return self._request("GET", "/api/config")

    # Get Platforms Endpoint GET: /api/platforms
    def get_platforms(self) -> Optional[List[Dict]]:
        """
        Retrieve list of platforms from ROMM.

        Returns:
            List of platforms
        """
        return self._request("GET", "/api/platforms")

    def get_collections(self) -> Optional[List[Dict]]:
        """
        Retrieve manually created collections.

        Returns:
            List of collections
        """
        return self._request("GET", "/api/collections")

    def get_virtual_collections(self) -> Optional[List[Dict]]:
        """
        Retrieve virtual collections.

        Returns:
            List of virtual collections
        """
        return self._request("GET", "/api/collections/virtual?type=collection")

    def get_platform_by_slug(self) -> Optional[int]:
        """
        Retrieve platform ID by configured slug.

        Returns:
            Platform ID if found, otherwise None
        """
        platforms = self.get_platforms()
        if platforms:
            for platform in platforms:
                if platform.get('fs_slug') == self.slug:
                    return platform.get('id')
        return None

    def filter_games(self,
                     platform_id: Optional[int] = None,
                     limit: Optional[int] = None,
                     offset: Optional[int] = None,
                     order_by: Optional[str] = None,
                     order_dir: Optional[str] = None,
                     **kwargs
                     ) -> Optional[List[Dict]]:
        """
        Filter games based on various parameters.

        Args:
            platform_id: Platform ID to filter by
            limit: Maximum number of games to return
            offset: Pagination offset
            order_by: Field to order results by
            order_dir: Direction of ordering (asc/desc)
            group_by_meta_id: Whether to group by meta ID
            **kwargs: Additional filter parameters

        Returns:
            List of filtered games
        """

        params = {}

        if platform_id is not None:
            params['platform_id'] = platform_id

        if limit is not None:
            params['limit'] = limit

        params.update(kwargs)

        return self._request("GET", "/api/roms", params=params)

