from re import S
from django.db import models
from datetime import datetime, timedelta

# Create your models here.


class myMessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(c_time__lt=(datetime.now()-timedelta(days=2)))


DELETE_SETTING = [
    (0, 'ATONCE'),
    (1, 'SESSION'),
    (2, 'ONEDAY'),
    (3, 'TWODAY'),
]


class myUser(models.Model):
    username = models.CharField(max_length=128, unique=True)
    setting = models.IntegerField(default=1, choices=DELETE_SETTING)
    password = models.CharField(
        max_length=128, null=True, blank=True, default='')
    c_time = models.DateTimeField(auto_now_add=True)
    friends = models.ManyToManyField("self")
    real_in_db = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def get_friends(self):
        print('get_friends')
        _friends = self.friends.values('username')
        _ = []
        for i in _friends:
            _.append(i['username'])
        return _

    def load_message(self, friend_name):
        pass


class myUserMessage(models.Model):
    from_user = models.ForeignKey(
        'myUser', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(
        'myUser', on_delete=models.CASCADE, related_name='to_user')
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    trash_data = myMessageManager()

    def __str__(self):
        return self.content


class myRoomMessage(models.Model):
    from_user = models.ForeignKey('myUser', on_delete=models.CASCADE)
    to_room = models.ForeignKey('myRoom', on_delete=models.CASCADE)
    content = models.CharField(max_length=1024)
    c_time = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    trash_data = myMessageManager()

    def __str__(self):
        return self.content

    def send(self):
        pass


class myRoom(models.Model):
    roomname = models.CharField(max_length=128, unique=True)
    auto_delete_setting = models.IntegerField(default=3)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.roomname

    def load_message(self):
        pass
