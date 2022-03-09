import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "H84.settings")  # project_name 项目名称
django.setup()

from channels.generic.websocket import WebsocketConsumer
from django.core.cache import cache
from asgiref.sync import async_to_sync
import json

from hour84.models import myUser, myRoom

import re


class online_user_list:
    def __init__(self):
        self.list = set()

    def add(self, elem):
        self.list.add(elem)

    def remove(self, elem):
        self.list.discard(elem)

    def match(self, elem):
        list_str = str(self.list)
        # print(list_str)
        res = re.findall("(?<=')[^, ]*?" + elem + ".*?(?=')", list_str)
        return res

    def __iter__(self):
        return self.list.__iter__()

    def __str__(self):
        return str(self.list)


ONLINE_USER = online_user_list()


class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        else:
            async_to_sync(self.channel_layer.group_send)(
                self.username,
                {
                    'type': 'group_send_event',
                    'data': data,
                }
            )

    def user_login_or_register(self, username, password, setting):  # entered the password
        print("user_login_or_register")
        resp = {
            'action': 'login',
            'status': True,
        }
        self.from_db = True
        # print(username, '-', password)
        user = myUser.objects.filter(username=username)
        if len(user):  # username has occured
            user = myUser.objects.filter(username=username, password=password)
            if not len(user):
                resp['status'] = False
                resp['reason'] = 'password is not correct'
        else:
            resp['action'] = 'register'
            myUser.objects.create(username=username, password=password, setting=setting)
        if username not in ONLINE_USER and resp['status']:
            self.has_login = True
            self.add_user_online(username)
        self.send(json.dumps(resp))

    def anonymous_user_login(self, username):  # didnt enter the password
        print("anonymous_user_login")
        user = myUser.objects.filter(username=username)
        resp = {
            'action': 'anonymous_login',
            'status': True
        }
        if len(user):
            resp['status'] = False
            resp['reason'] = 'username duplicated'
        if username not in ONLINE_USER and resp['status']:
            self.has_login = True
            self.add_user_online(username)
        self.send(json.dumps(resp))

    def add_user_online(self, username):
        self.username = username
        ONLINE_USER.add(self.username)
        cache.set('friend_%s' % self.username, [], None)
        cache.set('group_%s' % self.username, [], None)
        if self.from_db:
            self.load_user_from_db()

    def update_user_in_db(self, username):
        pass

    def load_user_from_db(self):
        user = myUser.objects.get(username=self.username)
        friends = user.friends.all()
        friend_list = []
        for it in friends:
            friend_list.append(it.username)
        cache.set('friend_%s' % self.username, friend_list)

    def remove_user_offline(self):
        ONLINE_USER.remove(self.username)
        cache.delete_many(['friend_%s' % self.username, 'group_%s' % self.username])

    def login_event(self, data):
        if data['password']:
            self.user_login_or_register(data['username'], data['password'], data['setting'])
        else:
            self.anonymous_user_login(data['username'])
        if self.has_login:
            async_to_sync(self.channel_layer.group_add)(self.username, self.channel_name)

    def search_event(self, data):
        print("search ....")
        content = data['content']
        obj = data['object']
        mathch_list = set()
        if obj == 'user':
            mathch_list |= set(ONLINE_USER.match(content))
            resp = list(myUser.objects.values('username', 'online').filter(username__contains=content).all())
            for it in resp:
                mathch_list.add((it['username']))
        else:
            resp = list(myRoom.objects.values('roomname').filter(roomname__contains=content).all())
            for it in resp:
                mathch_list.add(it['roomname'])
        print(mathch_list)
        self.send(json.dumps(list(mathch_list)))

    def message_event(self, data):
        print("message ...")
        pass
