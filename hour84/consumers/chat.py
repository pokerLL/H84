from socket import socket
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "H84.settings")  # project_name 项目名称
django.setup()

import re
from hour84.models import myUser, myRoom, myUserMessage, myRoomMessage
import json
from asgiref.sync import async_to_sync
from django.core.cache import cache
from channels.generic.websocket import WebsocketConsumer
from select import select
from django.db.models import Q
from django.conf import settings

import datetime
from hour84.views import getProfilePicUrl
from pathlib import Path



class CJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # 这里可以统一修改想要的格式
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            # 这里可以统一修改想要的格式
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj) 

class online_user_list:
    def __init__(self):
        self.list1 = set()  # for user not in db
        self.list2 = set()  # for user in db

    def add(self, elem, real_in_db):
        if real_in_db:
            self.list2.add(elem)
        else:
            self.list1.add(elem)

    def remove(self, elem, real_in_db):
        if real_in_db:
            self.list2.discard(elem)
        else:
            self.list1.discard(elem)

    def match(self, elem):
        list_str1 = str(self.list1)
        res1 = re.findall("(?<=')[^, ]*?" + elem + ".*?(?=')", list_str1)
        list_str2 = str(self.list2)
        res2 = re.findall("(?<=')[^, ]*?" + elem + ".*?(?=')", list_str2)
        res = res1 + res2
        return res

    def is_anonymous(self, elem):
        print(elem, " is_anonymous : ", (elem in self.list1))
        return (elem in self.list1)

    def __iter__(self):
        # return self.list.__iter__()
        pass

    def __str__(self):
        return str(self.list1)+str(self.list2)

    def __len__(self):
        return len(self.list1)+len(self.list2)


ONLINE_USER = online_user_list()


class Chat(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.friends = set()
        self.room = set()

    def onlineUserOperate(self, action, elem):
        if action == 'remove':  # only called by slef
            ONLINE_USER.remove(elem, self.user.real_in_db)
            for fr in self.friends:
                async_to_sync(self.channel_layer.group_send)(
                    'user-'+fr, {
                        'type': 'group_send_event',
                        'data': {
                            'action': 'friendlist_update',
                            '_type': 'offline',
                            'friend_name': self.user.username,
                        }
                    }
                )
            async_to_sync(self.channel_layer.group_send)(
                'ONLINE_USER', {
                    'type': 'group_send_event',
                    'data': {
                        'action': 'online_user_update',
                        '_type': 'user_offline',
                        'username': elem,
                    }
                })
        elif action == 'add':
            ONLINE_USER.add(elem, self.user.real_in_db)
            for fr in self.friends:
                async_to_sync(self.channel_layer.group_send)(
                    'user-'+fr, {
                        'type': 'group_send_event',
                        'data': {
                            'action': 'friendlist_update',
                            '_type': 'online',
                            'friend_name': self.user.username,
                        }
                    }
                )
            async_to_sync(self.channel_layer.group_send)(
                'ONLINE_USER', {
                    'type': 'group_send_event',
                    'data': {
                        'action': 'online_user_update',
                        '_type': 'user_online',
                        'username': elem,
                    }
                })
        elif action == 'match':
            return ONLINE_USER.match(elem)
        elif action == 'is_anonymous':
            return ONLINE_USER.is_anonymous(elem)
        else:
            print(action, ' operation to ONLINE_USER_SET : wrong')

    def connect(self):
        print('connect...')
        self.accept()

    def disconnect(self, close_code):
        print('disconnect...', close_code)
        if self.user:
            self.onlineUserOperate('remove', self.user.username)
            # async_to_sync(self.channel_layer.group_discard)()

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
        elif action == 'join_room':
            self.join_room_event(data)
        elif action == 'update_friendlist':
            self.update_friendlist_event(data)
        elif action == 'load_message':
            self.load_message_event(data)
        else:
            async_to_sync(self.channel_layer.group_send)(
                'user-'+self.user.username,
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
            'ONLINE_USER', self.channel_name)
        async_to_sync(self.channel_layer.group_add)(
            'user-'+self.user.username, self.channel_name)
        if self.user.real_in_db:
            self.friends = set(self.user.get_friends())
        self.onlineUserOperate('add', self.user.username)

    def search_event(self, data):
        print("search_event")
        print(data)
        _list = self.onlineUserOperate('match', data['content'])
        self.send(json.dumps({
            'action': 'search',
            'match_list': json.dumps(_list)
        }))

    def message_event(self, data):
        print("message_event")
        print(data)
        data['content'] =data['content'].strip()
        if data['_type'] == 'user':
            if self.user.real_in_db and not self.onlineUserOperate('is_anonymous', data['_to']):
                print('save user message')
                myUserMessage.objects.create(
                    from_user=self.user, to_user=myUser.objects.get(username=data['_to']), content=data['content'],act_time=data['_time'])
        elif data['_type'] == 'room':
            if self.user.username == data['_from'] and self.user.real_in_db:
                myRoomMessage.objects.create(
                    from_user=self.user, to_room=myRoom.objects.get(roomname=data['_to']), content=data['content'],act_time=data['_time'])

        async_to_sync(self.channel_layer.group_send)(
            data['_type']+'-'+data['_to'], {
                'type': 'group_send_event',
                'data': data,
            })

    def load_userinfo_event(self, data):
        print("load_userinfo_event")
        print('online :', ONLINE_USER)
        _len = len(ONLINE_USER)
        # _f = Path(getProfilePicUrl(self.user.username)).exists()
        resp = {
            'action': "load_userinfo",
            'userinfo': {
                'username': self.user.username,
                # 'has_profile_pic':_f,
                'real_in_db': self.user.real_in_db
            },
            'friends': json.dumps(list(self.friends)),
            'rooms': json.dumps([]),
            'online_usernum': _len
        }
        self.send(json.dumps(resp))

    def list_operation_event(self, data):
        print("list_operation_event")

    def app_status_updata(self):
        print("app_status_updata")

    def list_update(self):
        print("list_update")

    def join_room_event(self, data):
        print('join_room_event')
        print(data)
        async_to_sync(self.channel_layer.group_add)(
            'room-'+data['roomname'], self.channel_name)
        myRoom.objects.get_or_create(roomname=data['roomname'])

    def update_friendlist_event(self, data):
        print('update_friendlist_event')
        print(data)
        resp  =  {
            'action':'update_friendlist',
            '_type':data['_type'],
            'status':True
        }

        try:
            if data['_type']=='add':
                self.user.friends.add(myUser.objects.get(username=data['friend_name']))
            elif data['_type'] =='remove':
                self.user.friends.remove(myUser.objects.get(username=data['friend_name']))
        except:
            resp['status'] = False

        self.send(json.dumps(resp))

    def load_message_event(self, data):
        print("load_message_event")
        if data['_type'] == 'user':
            _users = [data['_from'], data['_to']]
            _messages = myUserMessage.objects.filter(Q(from_user__username__in=_users) & Q(
                to_user__username__in=_users)).values_list('from_user__username', 'to_user__username', 'content', 'act_time').order_by('act_time')
        elif data['_type'] == 'room':
            _messages = myRoomMessage.objects.filter(to_room__roomname=data['_to']).values_list('from_user__username', 'to_room__roomname', 'content', 'act_time').order_by('act_time')
        # print(list(_messages))
        self.send(json.dumps({
            'action': 'load_message',
            '_type': data['_type'],
            '_messages': list(_messages),
        }, cls=CJsonEncoder))
