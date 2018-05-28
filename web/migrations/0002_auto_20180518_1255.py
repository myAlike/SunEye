# Generated by Django 2.0.5 on 2018-05-18 04:55

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bind_hosts',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='web.BindHosts', verbose_name='授权主机'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='valid_begin_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 5, 18, 4, 55, 39, 303853, tzinfo=utc), help_text='yyyy-mm-dd HH:MM:SS'),
        ),
    ]