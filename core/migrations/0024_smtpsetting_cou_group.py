# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-06 22:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_auto_20160905_0115'),
    ]

    operations = [
        migrations.AddField(
            model_name='smtpsetting',
            name='cou_group',
            field=models.ManyToManyField(to='core.CoUserGroup', verbose_name='Group Availability'),
        ),
    ]