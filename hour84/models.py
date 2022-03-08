from django.db import models

# Create your models here.

DELETE_SETTING = [
    (0, 'ATONCE'),
    (1, 'SESSION'),
    (2, 'ONEDAY'),
    (3, 'TWODAY'),
]


class myUser(models.Model):
    uuid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, unique=True)
    auto_delete_setting = models.IntegerField(default=1, choices=DELETE_SETTING)
    account = models.CharField(max_length=128, null=True, blank=True, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=128, null=True, blank=True)
    birthday = models.DateField(max_length=128, null=True, blank=True)
    c_time = models.DateTimeField(auto_now_add=True)


class myUserMessage(models.Model):
    uuid = models.CharField(max_length=128, unique=True)
    from_user = models.ManyToManyField('myUser', related_name='from_user')
    to_user = models.ManyToManyField('myUser', related_name='to_user')
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)


class myRoomMessage(models.Model):
    uuid = models.CharField(max_length=128, unique=True)
    from_user = models.ManyToManyField('myUser')
    to_room = models.ManyToManyField('myRoom')
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)


class myRoom(models.Model):
    uuid = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=128, unique=True)
    auto_delete_setting = models.IntegerField(default=3)
    c_time = models.DateTimeField(auto_now_add=True)
