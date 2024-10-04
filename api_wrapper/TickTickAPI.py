#https://developer.ticktick.com/
import requests
from urllib.parse import urlencode
from typing import Literal

from .utils import ApiException

ApiException.set_api_name("TickTickAPI")


ProjectKind = Literal['task', 'note']
ProjectViewOptions = Literal['list', 'kanban', 'timeline']

TaskStatus = Literal["wont_do", "normal", "completed"]
TaskStatus_Map = {
    "wont_do": -1,
    "normal": 0,
    "completed": 2
}

TaskPriority = Literal["none", "low", "medium", "high"]
TaskPriority_Map = {
    "none": 0,
    "low": 1,
    "medium": 3,
    "high": 5
}

ChecklistItemStatus = Literal["normal", "completed"]
ChecklistItemStatus_Map = {
    "normal": 0,
    "completed": 1
}


class TickTickAPI:
    class Auth:
        def __init__(self, client_id:str, client_secret:str, redirect_uri:str, scopes:list =["read", "write"]):
            self.client_id = client_id
            self.client_secret = client_secret
            self.redirect_uri = redirect_uri
            self.scopes = []
            for scope in scopes:
                self.scopes.append(f'tasks:{scope}')
            self.scopes = ' '.join(self.scopes)


        def get_OAuth_url(self):
            url = 'https://ticktick.com/oauth/authorize'
            params = {
                'response_type': 'code',
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'scope': self.scopes,
            }
            return f"{url}?{urlencode(params)}"


        def get_access_token(self, code:str):
            url = 'https://ticktick.com/oauth/token'
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'scope': self.scopes,
                'redirect_uri': self.redirect_uri
            }
            response = requests.post(url, data=data)
            if response.status_code >= 300:
                raise ApiException(f'Failed to get access token: {response.text}')
            response = response.json()
            if not 'access_token' in response:
                raise ApiException(f'Failed to get access token: {response}')
            return response['access_token']

    ## Init

    def __init__(self, access_token:str=None):
        if access_token == None:
            raise ApiException.MissingAccessToken('TickTickAPI.Auth')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        self.root = "https://api.ticktick.com"

    ## Projects

    def get_projects(self):
        response = requests.get(self.root + '/open/v1/project', headers=self.headers)
        if response.status_code >= 300:
            raise ApiException(f'Failed to get projects: {response.text}')
        return response.json()
    

    def get_project(self, project_id:str):
        response = requests.get(self.root + f'/open/v1/project/{project_id}/data', headers=self.headers)
        if response.status_code >= 300:
            raise ApiException(f'Failed to get project: {response.text}')
        return response.json()
    

    def create_project(self, name:str, color:str=None, kind:ProjectKind='task', viewMode:ProjectViewOptions='list'):
        data = {
            'name': name,
            'kind': kind.upper(),
            'viewMode': viewMode.upper()
        }
        if color:
            data['color'] = color
        response = requests.post(self.root + '/open/v1/project', headers=self.headers, json=data)
        if response.status_code >= 300:
            raise ApiException(f'Failed to create project: {response.text}')
        return response.json()
    
    def update_project(self, project_id:str, name:str=None, color:str=None, kind:ProjectKind=None, viewMode:ProjectViewOptions=None):
        data = {}
        if name:
            data['name'] = name
        if color:
            data['color'] = color
        if kind:
            data['kind'] = kind
        if viewMode:
            data['viewMode'] = viewMode
        response = requests.post(self.root + f'/open/v1/project/{project_id}', headers=self.headers, json=data)
        if response.status_code >= 300:
            raise ApiException(f'Failed to update project: {response.text}')
        return response.json()
    

    def delete_project(self, project_id:str):
        response = requests.delete(self.root + f'/open/v1/project/{project_id}', headers=self.headers)
        if response.status_code >= 300:
            raise ApiException(f'Failed to delete project: {response.text}')
        return response.json()
    

    ## Tasks

    def get_tasks(self, project_id:str):
        try:
            project = self.get_project(project_id)
        except Exception as e:
            raise ApiException(f'Failed to get tasks: {e}')
        return project.get('tasks', [])
    

    def get_task(self, project_id:str, task_id:str):
        response = requests.get(self.root + f'/open/v1/project/{project_id}/task/{task_id}', headers=self.headers)
        if response.status_code >= 300:
            raise ApiException(f'Failed to get task: {response.text}')
        return response.json()
    

    def get_child_tasks(self, project_id:str, task_id:str):
        try:
            all_tasks = self.get_tasks(project_id)
            child_tasks = []
            for task in all_tasks:
                if task.get('parentId') == task_id:
                    child_tasks.append(task)
            return child_tasks
        except Exception as e:
            raise ApiException(f'Failed to get child tasks: {e}')


    def create_task(self, title:str, priority:TaskPriority="none",
                    project_id:str=None, 
                    content:str=None, 
                    desc:str=None, 
                    isAllDay:bool=False, 
                    startDate:str=None, 
                    dueDate:str=None, 
                    timeZone:str=None,
                    reminders:list=None,
                    sortOrder:int=None,
                    repeatFlag:str=None,
                    parentId:str=None
                ):
        data = {
            'title': title,
            'priority': TaskPriority_Map.get(priority, priority),
        }
        if project_id:
            data['projectId'] = project_id
        if content:
            data['content'] = content
        if desc:
            data['desc'] = desc
        if isAllDay:
            data['isAllDay'] = isAllDay
        if startDate:
            data['startDate'] = startDate
        if dueDate:
            data['dueDate'] = dueDate
        if timeZone:
            data['timeZone'] = timeZone
        if reminders:
            data['reminders'] = reminders
        if repeatFlag:
            data['repeatFlag'] = repeatFlag
        if sortOrder:
            data['sortOrder'] = sortOrder
        if parentId:
            data['parentId'] = parentId
        response = requests.post(self.root + f'/open/v1/task', headers=self.headers, json=data)
        if response.status_code >= 300:
            raise ApiException(f'Failed to create task: {response.text}')
        return response.json()
    

    def update_task(self, project_id:str, task_id:str, 
                    title:str=None, 
                    content:str=None, 
                    desc:str=None, 
                    isAllDay:bool=None, 
                    startDate:str=None, 
                    dueDate:str=None, 
                    timeZone:str=None,
                    status:TaskStatus=None,
                    reminders:list=None, 
                    repeatFlag:str=None,
                    sortOrder:int=None,
                    priority:TaskPriority=None,
                    items:list=None):
        data = {
            'id': task_id,
            'projectId': project_id
        }
        if title:
            data['title'] = title
        if content:
            data['content'] = content
        if desc:
            data['desc'] = desc
        if isAllDay:
            data['isAllDay'] = isAllDay
        if startDate:
            data['startDate'] = startDate
        if dueDate:
            data['dueDate'] = dueDate
        if timeZone:
            data['timeZone'] = timeZone
        if status:
            data['status'] = TaskStatus_Map.get(status, status)
        if reminders:
            data['reminders'] = reminders
        if repeatFlag:
            data['repeatFlag'] = repeatFlag
        if sortOrder:
            data['sortOrder'] = sortOrder
        if priority:
            data['priority'] = TaskPriority_Map.get(priority, priority)
        if items:
            data['items'] = items
        response = requests.post(self.root + f'/open/v1/task/{task_id}', headers=self.headers, json=data)
        if response.status_code >= 300:
            raise ApiException(f'Failed to update task: {response.text}')
        return response.json()


    def delete_task(self, project_id:str, task_id:str):
        response = requests.delete(self.root + f'/open/v1/project/{project_id}/task/{task_id}', headers=self.headers)
        if response.status_code >= 300:
            raise Exception(f'Failed to delete task: {response.text}')
        return response.json()


    def complete_task(self, project_id:str, task_id:str):
        response = requests.post(self.root + f'/open/v1/project/{project_id}/task/{task_id}/complete', headers=self.headers)
        if response.status_code >= 300:
            raise ApiException(f'Failed to complete task: {response.text}')
        return {'status': 'success'}
    

    def wont_do_task(self, project_id:str, task_id:str):
        try:
            child_tasks = self.get_child_tasks(project_id, task_id)
            for child in child_tasks:
                child_id = child.get("id", None)
                if not child_id:
                    continue
                if child.get("status", None) == 0:
                    self.update_task(project_id, child["id"], status="wont_do")
            return self.update_task(project_id, task_id, status="wont_do")
        except Exception as e:
            raise ApiException(f'Failed to set task to wont do: {e}')
    

    ## Checklist

    def get_checklist_items(self, project_id:str, task_id:str):
        try:
            task = self.get_task(project_id, task_id)
            return task.get('items', [])
        except Exception as e:
            raise ApiException(f'Failed to get checklist items: {e}')


    def create_checklist_item(self, project_id:str, task_id:str, title:list):
        try:
            items = self.get_checklist_items(project_id, task_id)
            for checklist_item in title:
                items.append({'title': checklist_item})
            return self.update_task(project_id, task_id, items=items)
        except Exception as e:
            raise ApiException(f'Failed to create checklist item: {e}')


    def complete_checklist_items(self, project_id:str, task_id:str, item_ids:list=None):
        try:
            items = self.get_checklist_items(project_id, task_id)
            if item_ids == None:
                for item in items:
                    item['status'] = ChecklistItemStatus_Map.get("completed")
            else:
                for item in items:
                    item_id = item.get('id', None)
                    if item_id in item_ids:
                        item['status'] = ChecklistItemStatus_Map.get("completed")
            return self.update_task(project_id, task_id, items=items)
        except Exception as e:
            raise ApiException(f'Failed to complete checklist items: {e}')

 
    def delete_checklist_item(self, project_id:str, task_id:str, item_id:list=None):
        try:
            items = self.get_checklist_items(project_id, task_id)
            if item_id == None:
                return self.update_task(project_id, task_id, items=[])
            for item in items:
                item_id = item.get('id', None)
                if item['id'] != item_id and item_id != None:
                    items.append(item)
            return self.update_task(project_id, task_id, items=items)
        except Exception as e:
            raise ApiException(f'Failed to delete checklist item: {e}')