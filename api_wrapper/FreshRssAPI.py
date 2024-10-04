#https://github.com/FreshRSS/FreshRSS/blob/edge/p/api/fever.php
import requests, hashlib

class FreshRssAPI:
    def __init__(self, base_url:str, username:str, password:str):
        base_url = base_url.removesuffix('/api/fever.php?api')
        self.base_url = base_url + "/api/fever.php?api"
        self.api_key = hashlib.md5(f"{username}:{password}".encode()).hexdigest()
        self.payload = {
            "api_key": self.api_key
        }

    
    def get_starred_item_ids(self):
        response = requests.post(f"{self.base_url}&saved_item_ids", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to get saved item IDs: {response.text}')
        data = response.json()
        items = data["saved_item_ids"]
        items = [item_id for item_id in items.split(",")]
        return items
    
    def get_feeds(self):
        response = requests.post(f"{self.base_url}&feeds", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to get feeds: {response.text}')
        data = response.json()
        feed_groups = data["feeds_groups"]
        feed_groups = [{"group_id": group["group_id"], "feed_ids": [int(feed_id) for feed_id in group["feed_ids"].split(",")]} for group in feed_groups]
        for feed in data["feeds"]:
            feed["group_id"] = next(group["group_id"] for group in feed_groups if feed["id"] in group["feed_ids"])
        return data["feeds"]
    
    def get_categories(self):
        response = requests.post(f"{self.base_url}&groups", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to get categories: {response.text}')
        data = response.json()
        feed_groups = data["feeds_groups"]
        feed_groups = [{"group_id": group["group_id"], "feed_ids": [int(feed_id) for feed_id in group["feed_ids"].split(",")]} for group in feed_groups]
        print(feed_groups)
        for group in data["groups"]:
            group["feed_ids"] = [feed_group["feed_ids"] for feed_group in feed_groups if feed_group["group_id"] == group["id"]]
        return data["groups"]
    
    def get_items(self, feed_ids:list=None, category_ids:list=None, id_only:bool=False, read:bool=None, starred:bool=None):
        url = f"{self.base_url}&items"
        if feed_ids:
            if type(feed_ids) != int and type(feed_ids) != str:
                feed_ids = ",".join(map(str, feed_ids))
                print(feed_ids)
            url += f"&feed_ids={feed_ids}"
        if category_ids:
            if type(category_ids) != int and type(category_ids) != str:
                category_ids = ",".join(map(str, category_ids))
            url += f"&group_ids={category_ids}"

        response = requests.post(url, data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to get feed items: {response.text}')
        data = response.json()
        if read == True:
            data["items"] = [item for item in data["items"] if item["is_read"] == 1]
        elif read == False:
            data["items"] = [item for item in data["items"] if item["is_read"] == 0]

        if starred == True:
            data["items"] = [item for item in data["items"] if item["is_saved"] == 1]
        elif starred == False:
            data["items"] = [item for item in data["items"] if item["is_saved"] == 0]

        if id_only:
            return [item["id"] for item in data["items"]]
        return data["items"]
    
    def get_item(self, item_id:list):
        if type(item_id) != int and type(item_id) != str:
            item_id = ",".join(map(str, item_id))
        response = requests.post(f"{self.base_url}&items&with_ids={item_id}", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to get item details: {response.text}')
        data = response.json()
        if len(data["items"]) > 0:
            return data["items"][0]
        return data["items"]
    
    # Actions
    
    def mark_item_as_read(self, item_id:int):
        response = requests.post(f"{self.base_url}&mark=item&as=read&id={item_id}", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to mark item as read: {response.text}')
        return response.json()
    
    def mark_item_as_unread(self, item_id:int):
        response = requests.post(f"{self.base_url}&mark=item&as=unread&id={item_id}", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to mark item as unread: {response.text}')
        return response.json()
    
    def mark_item_as_starred(self, item_id:int):
        response = requests.post(f"{self.base_url}&mark=item&as=saved&id={item_id}", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to mark item as starred: {response.text}')
        return response.json()
    
    def mark_item_as_unstarred(self, item_id:int):
        response = requests.post(f"{self.base_url}&mark=item&as=unsaved&id={item_id}", data=self.payload)
        if response.status_code != 200:
            raise Exception(f'[FreshRssAPI] Failed to mark item as unstarred: {response.text}')
        return response.json()