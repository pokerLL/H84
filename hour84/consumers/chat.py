from select import select
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "H84.settings")  # project_name 项目名称
django.setup()

from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache
from asgiref.sync import async_to_sync
import json
from hour84.models import myUser, myRoom
import re



class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def connect(self):
        print('connect...')
        self.accept()

    def disconnect(self, close_code):
        print('disconnect...', close_code)

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
        if(len(same_name_user) != 0): #
            if data['password'] == same_name_user[0].password:
                resp['status'] = True
                self.user = same_name_user[0]
            else:
                resp['reason'] = 'Username duplicated or Password is not correct'
        else:
            resp['status']  = True
            if data['password'] != '':
                self.user = myUser.objects.create(username=data['username'],
                                                  password=data['password'],
                                                  setting=data['setting'])
            else:
                self.user = myUser()
                self.user.username = data['username']
                self.user.real_in_db = False
        self.login_init()
        self.send(json.dumps(resp))

    def login_init(self):
        print("login_init")
        async_to_sync(self.channel_layer.group_add)(self.user.username,self.channel_name)
        self.friends = set()
        self.rooms = set()
        if self.user.real_in_db:
            self.friends = set(self.user.get_friends())



    def search_event(self, data):
        print("search_event")

    def message_event(self, data):
        print("message_event")
        async_to_sync(self.channel_layer.group_send)(
            data['_to'],{
            'type': 'group_send_event',
            'data': data,
        })

    def load_userinfo_event(self, data):
        print("load_userinfo_event")
        resp = {
            'action':"load_userinfo",
            'userinfo': {
                'username': self.user.username,
                'real_in_db': self.user.real_in_db
            },
            'friends': json.dumps(list(self.friends)),
            'rooms': json.dumps([])
        }
        self.send(json.dumps(resp))


    def list_operation_event(self, data):
        print("list_operation_event")

    def app_status_updata(self):
        print("app_status_updata")

    def list_update(self):
        print("list_update")