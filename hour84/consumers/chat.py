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
    
    
    def user_login_or_register(self, username,password,setting): # entered the password
        print("user_login_or_register")
        resp = {
                'action':'login',
                'status':True,
            }
        self.from_db = True
        print(username, '-', password)
        user = myUser.objects.filter(username=username)
        if len(user): # username has occured
            user = myUser.objects.filter(username=username, password=password)
            if not len(user):
                resp['status']=False
                resp['reason']='password is not correct'
        else:
            resp['action']='register'
            myUser.objects.create(username=username,password=password,setting=setting)
        if username not in ONLINE_USER and  resp['status']:
            self.add_user_online()
        self.send(json.dumps(resp))

    def anonymous_user_login(self,username): # didnt enter the password
        print("anonymous_user_login")
        user  = myUser.objects.filter(username=username)
        resp = {
                'action':'anonymous_login',
                'status':True
            }
        if len(user):
            resp['status']=False
            resp['reason']='username duplicated'
        if username not in ONLINE_USER and resp['status']:
            self.add_user_online(username)
        self.send(json.dumps(resp))

    def add_user_online(self,username):
        self.username=username
        ONLINE_USER.add(self.username)
        cache.set('friend_%s'%self.username,[],None)
        cache.set('group_%s'%self.username,[],None)
        if self.from_db:
            self.load_user_from_db()

    def update_user_in_db(self,username):
        pass
    
    def load_user_from_db(self):
        user = myUser.objects.get(username=self.username)
        friends = user.friends.all()
        friend_list = []
        for it in friends:
            friend_list.append(it.username)
        cache.set('friend_%s'%self.username,friend_list)
        print(friend_list)
        print(cache.get('friend_%s'%self.username))

    def remove_user_offline(self):
        cache.delete_many(['friend_%s'%self.username,'group_%s'%self.username])

    def login_event(self, data):
        if data['password']:
            self.user_login_or_register(data['username'], data['password'],data['setting'])
        else:
            self.anonymous_user_login(data['username'])

    def search_event(self, data):
        print("search ....")
        pass

    def message_event(self, data):
        print("message ...")
        pass
