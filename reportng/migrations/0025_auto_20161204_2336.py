# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-04 22:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportng', '0024_auto_20161204_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaildeliveryreport',
            name='sent_at',
            field=models.DateTimeField(null=True, verbose_name='Sent'),
        ),
    ]
