# Generated by Django 4.0.3 on 2022-03-08 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hour84', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myuser',
            old_name='name',
            new_name='username',
        ),
        migrations.RemoveField(
            model_name='myuser',
            name='account',
        ),
    ]
