from django.urls import path
from hour84.consumers.chat import Chat

websocket_urlpatterns = [
    path('wss/chat',Chat.as_asgi()),

]
