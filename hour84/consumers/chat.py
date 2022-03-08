from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.cache import cache
import json

import os

# from hour84.models import myUser


class Chat(AsyncWebsocketConsumer):

    async def connect(self):
        print('connect...')
        await self.accept()

    async def disconnect(self,close_code):
        print('disconnect...',close_code)

    async def group_send_event(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))

    # event router
    async def receive(self,text_data):
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
                    self.room_group_name,
                    {
                        'type'      : 'group_send_event',
                        'data'   : data,
                    }
            )
    
    def db_get_user(username='',password=None):
	return True

    async def add_user_online():
	if not cache.get('alluser_online'):
	    cache.set('alluser_online',[],None)
	pass

    def update_user_in_db(username):
	pass

    async def remove_user_offline():
	pass

    async def login_event(self, data):
        print('login....')
	self.username=data['username']
        if 'password' in data.keys():
            user = self.db_get_user(username=data['username'],password=data['password']):
	    if user:
		self.update_user_in_db()
	    self.add_user_online()
        else:
	    user = self.db_get_user(username=username)
	    if not user:
		self.username=username
		add_user_online()

    async def search_event(self, data):
        print("search ....")
        pass

    async def message_event(self, data):
        print("message ...")
        pass
