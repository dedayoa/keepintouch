# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-18 18:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gomez', '0023_kitsystem_max_standard_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kitsystem',
            name='user_phone_as_callerid',
        ),
    ]
