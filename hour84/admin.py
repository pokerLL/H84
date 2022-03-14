from django.contrib import admin

# Register your models here.
from hour84.models import *


class MyUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'password']

class myRoomAdmin(admin.ModelAdmin):
    list_display = ['roomname']


class myUserMessageAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user','content']


class myRoomMessageAdmin(admin.ModelAdmin):
    list_display = ['to_room', 'from_user','content']


admin.site.register(myUser, MyUserAdmin)
admin.site.register(myRoom, myRoomAdmin)
admin.site.register(myUserMessage, myUserMessageAdmin)
admin.site.register(myRoomMessage, myRoomMessageAdmin)

