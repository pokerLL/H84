from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.cache import cache
import json

import os
ONLINE_USER = 'chat_online_user'

from hour84.models import myUser


class Chat(AsyncWebsocketConsumer):

    async def connect(self):
        self.username = '10086'
        print('connect...')
        await self.accept()

    async def disconnect(self,close_code):
        print('disconnect...',close_code)

    async def group_send_event(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))

    # event router
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action','')
        print(data)

        if action == 'login':
            await self.login_event(data)
        elif action == 'search':
            await self.search_event(data)
        elif action == 'message':
            await self.message_event(data)
        else:
            await self.channel_layer.group_send(
                    self.username,
                    {
                        'type': 'group_send_event',
                        'data': data,
                    }
            )
    
    @database_sync_to_async
    def user_login_or_register(self, username='',password=None):
        print("user_login_or_register")
        FLAG = False
        print(username, '-', password)
        user = myUser.objects.filter(username=username)
        if len(user):
            user = myUser.objects.filter(username=username, password=password)
            if len(user):
                FLAG = True
        else:
            FLAG = True
            myUser.objects.create(username=username, password=password)

        if FLAG:
            print('ttt')
            self.username = username
            self.add_user_online()
            online_user_num = len(cache.get(ONLINE_USER, []))
            self.send(text_data=json.dumps({
                'code': 200,
                'online_user_num': online_user_num,
            }))
        else:
            print('fff')
            self.send(text_data=json.dumps({
                'code': 400,
            }))

    @database_sync_to_async
    def anonymous_user_login(self):
        print("anonymous_user_login")

    async def add_user_online(self):
        online_user_list = cache.get(ONLINE_USER,None)
        if not online_user_list:
            cache.set(ONLINE_USER,[],None)
        cache.set(ONLINE_USER,online_user_list.append(self.username),None)
        cache.set('friend_%s'%self.username,[],None)
        cache.set('group_%s'%self.username,[],None)

    async def update_user_in_db(username):
        pass

    async def remove_user_offline(self):
        online_user_list = cache.get(ONLINE_USER,None)
        if not online_user_list:
            return
        cache.set(ONLINE_USER,online_user_list.remove(self.username),None)
        cache.delete_many(['friend_%s'%self.username,'group_%s'%self.username])

    async def login_event(self, data):
        if 'password' in data.keys():
            await self.user_login_or_register(data['username'], data['password'])
        else:
            await self.anonymous_user_login()

    async def search_event(self, data):
        print("search ....")
        pass

    async def message_event(self, data):
        print("message ...")
        pass
