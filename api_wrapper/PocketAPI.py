#https://getpocket.com/developer/docs/
import requests
from urllib.parse import parse_qsl
from typing import Literal

from .utils import ApiException

ApiException.set_api_name("PocketAPI")

ItemState = Literal["unread", "archive", "all", "all_and_deleted"]
ItemTag = Literal["__untagged__"]
ItemContentType = Literal["article", "video", "image"]
ItemSort = Literal["newest", "oldest", "title", "site"]
ItemDetailType = Literal["simple", "complete"]

class PocketAPI:
    class OAuth:
        def __init__(self, consumer_key, redirect_uri):
            self.consumer_key = consumer_key
            self.redirect_uri = redirect_uri
            self.code = None

        def __request_token(self):
            url = "https://getpocket.com/v3/oauth/request"
            data = {
                "consumer_key": self.consumer_key,
                "redirect_uri": self.redirect_uri
            }
            try:
                response = requests.post(url, json=data)
                if response.status_code >= 300:
                    raise Exception(response.text)
                response = dict(parse_qsl(response.text))
                code = response["code"]
                self.code = code
                return code
            except Exception as error:
                raise ApiException(f"Failed to get request token: {error}")
        
        def get_OAuth_url(self):
            request_token = self.__request_token()
            return f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={self.redirect_uri}"

        def get_access_token(self):
            if self.code is None:
                raise ApiException("Please authorize the application first. Use the 'get_OAuth_url' method to get the authorization URL.")
            url = "https://getpocket.com/v3/oauth/authorize"
            data = {
                "consumer_key": self.consumer_key,
                "code": self.code
            }
            response = requests.post(url, json=data)
            if response.status_code >= 300:
                raise ApiException(f'Failed to get access token: {response.text}')
            response = dict(parse_qsl(response.text))
            return response["access_token"]
        
        def OAuth_flow(self):
            print(self.get_OAuth_url())
            input("Press Enter after successful callback...")
            return self.get_access_token()
    

    ## Init

    def __init__(self, customer_key, access_token=None):
        if access_token == None:
            raise ApiException.MissingAccessToken("PocketAPI.OAuth")
        self.access_token = access_token
        self.customer_key = customer_key
        self.base_url = "https://getpocket.com/v3"

    def __append_auth(self, data):
        data["consumer_key"] = self.customer_key
        data["access_token"] = self.access_token
        return data
    

    def get_items(self, 
                state:ItemState="all",
                favorite:bool=None,
                tag:ItemTag=None,
                content_type:ItemContentType=None,
                sort:ItemSort="newest",
                detailType:ItemDetailType="simple",
                search:str=None,
                domain:str=None,
                since:int=None,
                count:int=30, 
                offset:int=0):
        if count > 30:
            raise ApiException("The maximum number of items to retrieve is 30.")
        data = {
            "state": "all" if state == "all_and_deleted" else state,
            "sort": sort,
            "detailType": detailType,
            "count": count,
            "offset": offset
        }
        if favorite is not None:
            favorite = "1" if favorite else "0"
            data["favorite"] = favorite
        if tag:
            data["tag"] = tag
        if content_type:
            data["contentType"] = content_type
        if search:
            data["search"] = search
        if domain:
            data["domain"] = domain
        if since:
            data["since"] = since
        data = self.__append_auth(data)
        response = requests.post(self.base_url + "/get", json=data)
        if response.status_code >= 300:
            raise ApiException(f"Failed to get items: {response.text}")
        response = response.json()
        if state == "all":
            item_list = {}
            for item_id, item in response["list"].items():
                if item["status"] == "2":
                    continue
                item_list[item_id] = item
            response["list"] = item_list
        return response
    

    def add_item(self, url:str, title:str=None, tags:list[str]=None):
        data = {
            "url": url
        }
        if title:
            data["title"] = title
        if tags:
            data["tags"] = ",".join(tags)
        data = self.__append_auth(data)
        response = requests.post(self.base_url + "/add", json=data)
        if response.status_code >= 300:
            raise ApiException(f"Failed to add item: {response.text}")
        return response.json()
    

    def modify_item(self, item_id:int, archive:bool=None, favorite:bool=None, delete:bool=None, add_tags:list[str]=None, remove_tags:list[str]=None, set_tags:bool=None, clear_tags:bool=None):
        data = {
            "actions": [],
            "item_id": item_id
        }
        if archive is not None:
            action = {"action": "archive" if archive else "readd", "item_id": item_id}
            data["actions"].append(action)
        if favorite is not None:
            action = {"action": "favorite" if favorite else "unfavorite", "item_id": item_id}
            data["actions"].append(action)
        if delete:
            action = {"action": "delete", "item_id": item_id}
            data["actions"].append(action)
        
        if clear_tags:
            action = {"action": "tags_clear", "item_id": item_id}
            data["actions"].append(action)
        if remove_tags:
            action = {"action": "tags_remove", "item_id": item_id, "tags": ",".join(remove_tags)}
            data["actions"].append(action)
        if set_tags:
            action = {"action": "tags_replace", "item_id": item_id, "tags": ",".join(set_tags)}
            data["actions"].append(action)
        if add_tags:
            action = {"action": "tags_add", "item_id": item_id, "tags": ",".join(add_tags)}
            data["actions"].append(action)

        data = self.__append_auth(data)
        response = requests.post(self.base_url + "/send", json=data)
        if response.status_code >= 300:
            raise ApiException(f"Failed to modify item: {response.text}")
        return response.json()