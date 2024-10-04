class ApiException(Exception):
    _api_name = None

    @classmethod
    def set_api_name(cls, api_name):
        cls._api_name = api_name

    def __init__(self, message):
        self.message = message
        super().__init__(self.format_message())

    def format_message(self):
        if self._api_name is None:
            raise Exception(self.message)
        raise Exception (f"\033[94m[{self._api_name}]\033[0m {self.message}")
    
    class MissingAccessToken(Exception):
        def __init__(self, auth_class):
            message = f"Please provide an access token. You can get one by using the '{auth_class}' class."
            super().__init__(ApiException(message))