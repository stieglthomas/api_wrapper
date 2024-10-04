# https://developers.home-assistant.io/docs/api/rest/
import requests
from .utils import ApiException

ApiException.set_api_name("HassAPI")

class HassAPI:
    def __init__(self, base_url:str, access_token:str):
        base_url = base_url.removesuffix('/api/')
        self.base_url = f'{base_url}/api'
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }


    def get_state(self, entity_id:str):
        url = f"{self.base_url}/states/{entity_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise ApiException(f'Failed to get state of "{entity_id}": {response.text}')
        response = response.json()
        if entity_id.split('.')[0] == 'light':
            try:
                brightness = int(response['attributes']['brightness'])
                brightness_pct = round(brightness / 255 * 100)
            except:
                brightness_pct = None
            response['attributes']['brightness_pct'] = brightness_pct
        return response
    

    def call_service(self, service:str, entity_id:str=None, service_data:dict={}):
        domain, service_name = service.split('.')
        url = f"{self.base_url}/services/{domain}/{service_name}"
        if entity_id:
            if not entity_id.startswith(domain + '.'):
                entity_id = f"{domain}.{entity_id.rsplit('.', 1)[-1]}"
            service_data['entity_id'] = entity_id
        response = requests.post(url, headers=self.headers, json=service_data)
        if response.status_code != 200:
            raise ApiException(f'Failed to call service "{service}": {response.text}')
        return response.json()
    

    def activate_script(self, script_name:str, await_response:bool=True):
        if not script_name.startswith('script.'):
            script_name = f"script.{script_name}"#
        if await_response:
            return self.call_service(script_name)
        else:
            return self.call_service("script.turn_on", entity_id=script_name)
    

    def trigger_automation(self, automation_name:str, skip_condition:bool=False):
        return self.call_service(f"automation.{automation_name}", "trigger", {"skip_condition": skip_condition})
    

    def activate_scene(self, scene_name:str):
        if not scene_name.startswith('scene.'):
            scene_name = f"scene.{scene_name}"
        response = self.call_service("scene.turn_on", entity_id=scene_name)
        if response == []:
            raise ApiException(f'Scene "{scene_name}" not found')
        return response


    def fire_event(self, event_name:str, event_data:dict={}):
        url = f"{self.base_url}/events/{event_name}"
        response = requests.post(url, headers=self.headers, json=event_data)
        return response.json()