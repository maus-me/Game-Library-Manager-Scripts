import logging

import requests

logger = logging.getLogger(__name__)


class RommAPI:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def _request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            if resp.content:
                return resp.json()
            return None
        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            raise

    def authenticate(self, username, password):
        data = {"username": username, "password": password}
        result = self._request("POST", "/api/auth/login", json=data)
        token = result.get("access_token")
        self.session.headers.update({'Authorization': f'Bearer {token}'})
        return token

    def get_games(self, params=None):
        return self._request("GET", "/api/games", params=params)

    def add_game(self, game_data):
        return self._request("POST", "/api/games", json=game_data)

    def get_game(self, game_id):
        return self._request("GET", f"/api/games/{game_id}")

    def update_game(self, game_id, game_data):
        return self._request("PUT", f"/api/games/{game_id}", json=game_data)

    def delete_game(self, game_id):
        resp = self._request("DELETE", f"/api/games/{game_id}")
        return resp is None  # DELETE returns no content on success

    def request(self, method, endpoint, **kwargs):
        """
        Generic method to access any ROMM API endpoint.
        Example: api.request("GET", "/api/platforms")
        """
        return self._request(method, endpoint, **kwargs)
