# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-08 09:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0013_auto_20160905_1927'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='failedkitmessage',
            options={'verbose_name': 'Message'},
        ),
    ]
