# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-27 03:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0022_auto_20160927_0415'),
    ]

    operations = [
        migrations.AddField(
            model_name='standardmessaging',
            name='cc_recipients_send_email',
            field=models.BooleanField(default=True, verbose_name='Send Email'),
        ),
        migrations.AddField(
            model_name='standardmessaging',
            name='cc_recipients_send_sms',
            field=models.BooleanField(default=True, verbose_name='Send SMS'),
        ),
    ]
