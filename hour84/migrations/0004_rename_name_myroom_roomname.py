# Generated by Django 4.0.3 on 2022-03-09 05:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hour84', '0003_remove_myroom_uuid_remove_myroommessage_uuid_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='myroom',
            old_name='name',
            new_name='roomname',
        ),
    ]
