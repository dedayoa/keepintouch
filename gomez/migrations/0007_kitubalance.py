# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-23 19:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20160823_2012'),
        ('gomez', '0006_auto_20160823_1103'),
    ]

    operations = [
        migrations.CreateModel(
            name='KITUBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sms_balance', models.PositiveIntegerField(default=0)),
                ('free_sms_balance', models.PositiveIntegerField(default=0)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('kit_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.KITUser')),
            ],
        ),
    ]
