# Generated by Django 2.0.5 on 2018-05-18 04:59

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20180518_1255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='bind_hosts',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='valid_begin_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 18, 4, 59, 45, 691207, tzinfo=utc), help_text='yyyy-mm-dd HH:MM:SS'),
        ),
    ]
