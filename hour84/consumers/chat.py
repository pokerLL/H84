from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
import json



# from hour84.models import myUser


class Chat(AsyncWebsocketConsumer):

    async def connect(self):
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
                        'type'      : 'chat_message',
                        'data'   : data,
                    }
            )
    
    

    async def login_event(self, data):
        print('login....')
        username = data['username']
        if 'password' in data.keys():
            # same_name_user = myUser.objects.get(username=username)
            # if same_name_user: # login failure
            #    pass
            # user = myUser.objects.get(username=username,password=password)
            # if user: # login success
            #    pass
            # else: # need register
            #    same_name_user = myuser.objects.get(username=username)
            #    if same_name_user: # failure
            #        pass
            #    else: # register
            #        pass
            #    pass
            pass
        else:
            # self.username=username
            # await database_sync_to_async(create_user_in_db)({'username':username})
            pass

   # def get_user_from_db(username,password):
   #     return myUser.objects.get(username=username,password=password)

   # def create_user_in_db(data):
   #     return myUser.objects.create(**data)


    async def search_event(self, data):
        print("search ....")
        pass

    async def message_event(self, data):
        print("message ...")
        pass
