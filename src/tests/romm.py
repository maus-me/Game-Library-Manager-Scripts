from src.modules.api.romm import RommAPI


class RommTestAPI(RommAPI):
    @staticmethod
    def test():
        """Test various API endpoints."""
        api = RommAPI()
        api.heartbeat()
        # api.get_game_by_id(38567)
        api.get_profile()
        api.get_config()
        api.get_collections()
        api.get_virtual_collections()
        api.get_platform_by_slug()
        api.filter_games()
