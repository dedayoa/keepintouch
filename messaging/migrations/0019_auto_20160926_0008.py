# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-25 23:08
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0018_advancedmessaging_custom_data_namespace'),
    ]

    operations = [
        migrations.AddField(
            model_name='advancedmessaging',
            name='repeat_until',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2016, 9, 25, 23, 8, 49, 246558, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='advancedmessaging',
            name='contact_group',
            field=models.ManyToManyField(to='core.ContactGroup', verbose_name='Contact List'),
        ),
        migrations.AlterField(
            model_name='advancedmessaging',
            name='custom_data_namespace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.CustomData'),
        ),
    ]
