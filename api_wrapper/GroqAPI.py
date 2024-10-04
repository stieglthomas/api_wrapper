# https://console.groq.com/docs/quickstart
import requests
from .utils import ApiException

ApiException.set_api_name("GroqAPI")

class GroqAPI:
    def __init__(self, api_token:str, standard_model_id:str=None, standard_temperature:float=None, standard_max_tokens:int=None):
        self.root_url = "https://api.groq.com/openai/v1"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.model_id = standard_model_id
        self.temperature = standard_temperature
        self.max_tokens = standard_max_tokens


    def get_models(self):
        url = f"{self.root_url}/models"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ApiException(f'Failed to get models: {response.text}')
        return response.json()


    def chat_completion(self, messages:list, model_id:str=None, temperature:float =None, max_tokens:int=None):
        model_id = model_id or self.model_id
        if not model_id:
            raise ApiException(f'Please provide a model-ID (https://console.groq.com/docs/models)')
        roles = {message.get('role') for message in messages}
        if 'system' not in roles or 'user' not in roles:
            raise ApiException(f'Please provide at least one message with role "system" or "user"')

        url = f"{self.root_url}/chat/completions"
        data = {
            'model': model_id,
            'messages': messages,
            **({'temperature': temperature or self.temperature} if temperature or self.temperature else {}),
            **({'max_tokens': max_tokens or self.max_tokens} if max_tokens or self.max_tokens else {})
        }
        response = requests.post(url, headers=self.headers, json=data)
        if response.status_code != 200:
            raise ApiException(f'Failed to get chat completion: {response.text}')
        return response.json()