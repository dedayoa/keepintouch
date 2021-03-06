# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-15 13:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0006_auto_20160814_2145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runningmessage',
            name='sent_details',
        ),
        migrations.AddField(
            model_name='runningmessage',
            name='last_event_on',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 15, 13, 52, 7, 89409, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='reminder',
            name='delta_type',
            field=models.CharField(choices=[('day', 'Days'), ('week', 'Weeks'), ('month', 'Months'), ('year', 'Years')], default='day', max_length=20),
        ),
    ]
