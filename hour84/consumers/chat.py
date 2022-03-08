from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.core.cache import cache
import json

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'H84.settings')

from hour84.models import myUser


class Chat(AsyncWebsocketConsumer):

    async def connect(self):
        if 'online_user' not in cache.keys('user_*'):
            cache.set('online_user',[],None)
        print('connect...')
        # await self.accept()
        self.room_name = "10086"
        self.room_group_name = "room_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name,self.channel_name)
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
    
    

    async def login_event(self, data):
        print('login....')
        username = data['username']
        if 'password' in data.keys():
            pass
        else:
            pass


    async def search_event(self, data):
        print("search ....")
        pass

    async def message_event(self, data):
        print("message ...")
        pass
