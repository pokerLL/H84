from channels.generic.websocket import AsyncWebsocketConsumer
import json

class Chat(AsyncWebsocketConsumer):
    async def connect(self):
        print('connect...')
        await self.accept()
        self.room_name = "room1"
        await self.channel_layer.group_add(self.room_name,self.channel_name)

    async def disconnect(self,code):
        print('disconnect...',code)

    async def receive(self,data):
        data = json.loads(data)
        print(data)
        await self.channel_layer.group_send(self.room_data,data)

