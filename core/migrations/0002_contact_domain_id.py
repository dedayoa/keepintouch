# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-02 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='domain_id',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
    ]