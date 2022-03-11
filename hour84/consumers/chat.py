import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "H84.settings")  # project_name 项目名称
django.setup()

import re
from hour84.models import myUser, myRoom
import json
from asgiref.sync import async_to_sync
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer


class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = False
        self.from_db = False
        self.has_login = False

    def connect(self):
        print('connect...')
        self.accept()

    def disconnect(self, close_code):
        print('disconnect...', close_code)
        if self.username:
            self.remove_user_offline()

    def group_send_event(self, event):
        data = event['data']
        self.send(json.dumps(data))

    # event router
    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action', '')
        print(data)

        if action == 'login':
            self.login_event(data)
        elif action == 'search':
            self.search_event(data)
        elif action == 'message':
            self.message_event(data)
        elif action == 'load_userinfo':
            self.load_userinfo_event(data)
        elif action == 'list_operation':
            self.list_operation_event(data)
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.username,
                {
                    'type': 'group_send_event',
                    'data': data,
                }
            )

    def login_event(self, data):
        print("login_event")

    def search_event(self, data):
        print("search_event")

    def message_event(self, data):
        print("message_event")

    def load_userinfo_event(self, data):
        print("load_userinfo_event")

    def list_operation_event(self, data):
        print("list_operation_event")

    def app_status_updata(self):
        print("app_status_updata")

    def list_update(self):
        print("list_update")
