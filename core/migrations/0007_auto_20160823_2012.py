# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-23 19:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_kituser_free_sms_balance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kituser',
            name='free_sms_balance',
        ),
        migrations.RemoveField(
            model_name='kituser',
            name='sms_balance',
        ),
    ]
