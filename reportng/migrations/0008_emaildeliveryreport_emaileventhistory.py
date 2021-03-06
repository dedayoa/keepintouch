# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-05 09:51
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('reportng', '0007_auto_20160914_2239'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailDeliveryReport',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('batch_id', models.UUIDField(db_index=True, editable=False, help_text='A.K.A Process ID or Bulk ID', null=True)),
                ('to_email', models.EmailField(max_length=254)),
                ('from_email', models.EmailField(max_length=254)),
                ('email_message', django.contrib.postgres.fields.jsonb.JSONField()),
                ('email_gateway', django.contrib.postgres.fields.jsonb.JSONField()),
                ('msg_status', models.CharField(choices=[('0', 'SENT'), ('1', 'PROCESSED'), ('2', 'DROPPED'), ('3', 'DEFERRED'), ('4', 'DELIVERED'), ('5', 'BOUNCED')], default='', max_length=20)),
                ('kituser_id', models.IntegerField(db_index=True)),
                ('kitu_parent_id', models.IntegerField(db_index=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailEventHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('message_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reportng.EmailDeliveryReport')),
            ],
        ),
    ]
