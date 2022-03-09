import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "H84.settings")# project_name 项目名称
django.setup()

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.core.cache import cache
import json

import os
ONLINE_USER = set()

from hour84.models import myUser


class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.from_db = False
        self.username = '084660587'

    def connect(self):
        print('connect...')
        self.accept()

    def disconnect(self,close_code):
        print('disconnect...',close_code)

    def group_send_event(self, event):
        data = event['data']
        self.send(text_data=json.dumps(data))

    # event router
    def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action','')
        print(data)

        if action == 'login':
            self.login_event(data)
        elif action == 'search':
            self.search_event(data)
        elif action == 'message':
            self.message_event(data)
        else:
            self.channel_layer.group_send(
                    self.username,
                    {
                        'type': 'group_send_event',
                        'data': data,
                    }
            )
    
    def user_login_or_register(self, username='',password=None):
        print("user_login_or_register")
        resp = {
                'action':'login',
                'status':True,
            }
        print(username, '-', password)
        user = myUser.objects.filter(username=username)
        if len(user): # username has occured
            user = myUser.objects.filter(username=username, password=password)
            if len(user): # regular user login success
                pass
            elif password: # password is not correct
                resp['status']=False
                resp['reason']='password is not correct'
            else: # dont input a passwod and username is duplicated
                resp['action']= 'register'
                resp['status']= False
                resp['reason']='depulicate username'
        elif password: # user register
            resp['action'] = 'register'
            myUser.objects.create(username=username, password=password)
        if resp['status']:
            self.add_user_online(username)
            if resp['action'] == 'login':
                self.load_user_from_db()
        self.send(json.dumps(resp))

    def anonymous_user_login(self):
        print("anonymous_user_login")

    def add_user_online(self,username):
        self.username=username
        ONLINE_USER.add(self.username)
        cache.set('friend_%s'%self.username,[],None)
        cache.set('group_%s'%self.username,[],None)

    def update_user_in_db(self,username):
        pass
    
    def load_user_from_db(self):
        user = myUser.objects.get(username=self.username)
        friends = user.friends.all()
        print(friends)

    def remove_user_offline(self):
        cache.delete_many(['friend_%s'%self.username,'group_%s'%self.username])

    def login_event(self, data):
        self.user_login_or_register(data['username'], data['password'])

    def search_event(self, data):
        print("search ....")
        pass

    def message_event(self, data):
        print("message ...")
        pass
