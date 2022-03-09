from django.contrib import admin

# Register your models here.
from hour84.models import *



class MyUserAdmin(admin.ModelAdmin):
    list_display = ['username','password']


admin.site.register(myUser,MyUserAdmin)
admin.site.register(myUserMessage)
admin.site.register(myRoomMessage)
admin.site.register(myRoom)