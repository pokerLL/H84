from channels.generic.websocket import AsyncWebsocketConsumer
import json

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

    async def receive(self,text_data):
        data = json.loads(text_data)
        print(data)
        # data = text_data
        print(self.room_name)
        # await self.channel_layer.group_send(self.room_name,data)
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type'      : 'chat_message',
                    'data'   : data,
                }
        )

    async def chat_message(self, event):
        data = event['data']
        await self.send(text_data=json.dumps(data))

