from socket import socket
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
from select import select


class online_user_list:
    def __init__(self):
        self.list = set()

    def add(self, elem):
        self.list.add(elem)

    def remove(self, elem):
        self.list.discard(elem)

    def match(self, elem):
        list_str = str(self.list)
        res = re.findall("(?<=')[^, ]*?" + elem + ".*?(?=')", list_str)
        return res

    def __iter__(self):
        return self.list.__iter__()

    def __str__(self):
        return str(self.list)
    
    def __len__(self):
        return len(self.list)


ONLINE_USER = online_user_list()

class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def connect(self):
        print('connect...')
        self.accept()

    def disconnect(self, close_code):
        print('disconnect...', close_code)
        if self.user:
            ONLINE_USER.remove(self.user.username)

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
                self.user.username,
                {
                    'type': 'group_send_event',
                    'data': data,
                }
            )

    def login_event(self, data):
        print("login_event")
        resp = {
            'action': 'login',
            'status': False
        }
        same_name_user = myUser.objects.filter(username=data['username'])
        if(len(same_name_user) != 0):
            if data['password'] == same_name_user[0].password:
                resp['status'] = True
                self.user = same_name_user[0]
            else:
                resp['reason'] = 'Username duplicated or Password is not correct'
        else:
            resp['status'] = True
            if data['password'] != '':
                self.user = myUser.objects.create(username=data['username'],
                                                  password=data['password'],
                                                  setting=data['setting'])
            else:
                self.user = myUser()
                self.user.username = data['username']
                self.user.real_in_db = False
        if self.user:
            self.login_init()
        self.send(json.dumps(resp))

    def login_init(self):
        print("login_init")
        async_to_sync(self.channel_layer.group_add)(
            self.user.username, self.channel_name)
        self.friends = set()
        self.rooms = set()
        ONLINE_USER.add(self.user.username)
        if self.user.real_in_db:
            self.friends = set(self.user.get_friends())

    def search_event(self, data):
        print("search_event")
        print(data)
        _list = ONLINE_USER.match(data['content'])
        self.send(json.dumps({
            'action':'search',
            'match_list':json.dumps(_list)
        }))

    def message_event(self, data):
        print("message_event")
        async_to_sync(self.channel_layer.group_send)(
            data['_to'], {
                'type': 'group_send_event',
                'data': data,
            })

    def load_userinfo_event(self, data):
        print("load_userinfo_event")
        print(ONLINE_USER)
        _len = len(ONLINE_USER)
        resp = {
            'action': "load_userinfo",
            'userinfo': {
                'username': self.user.username,
                'real_in_db': self.user.real_in_db
            },
            'friends': json.dumps(list(self.friends)),
            'rooms': json.dumps([]),
            'online_usernum':_len
        }
        self.send(json.dumps(resp))

    def list_operation_event(self, data):
        print("list_operation_event")

    def app_status_updata(self):
        print("app_status_updata")

    def list_update(self):
        print("list_update")
