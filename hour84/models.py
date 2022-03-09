from django.db import models

# Create your models here.

DELETE_SETTING = [
    (0, 'ATONCE'),
    (1, 'SESSION'),
    (2, 'ONEDAY'),
    (3, 'TWODAY'),
]


class myUser(models.Model):
    username = models.CharField(max_length=128, unique=True)
    auto_delete_setting = models.IntegerField(default=1, choices=DELETE_SETTING)
    password = models.CharField(max_length=128, null=True, blank=True)
    gender = models.CharField(max_length=128, null=True, blank=True)
    birthday = models.DateField(max_length=128, null=True, blank=True)
    c_time = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField("self")

    def __str__(self):
        return self.username

class myUserMessage(models.Model):
    from_user = models.ManyToManyField('myUser', related_name='from_user')
    to_user = models.ManyToManyField('myUser', related_name='to_user')
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content


class myRoomMessage(models.Model):
    from_user = models.ManyToManyField('myUser')
    to_room = models.ManyToManyField('myRoom')
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.content


class myRoom(models.Model):
    roomname = models.CharField(max_length=128, unique=True)
    auto_delete_setting = models.IntegerField(default=3)
    c_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.roomname
