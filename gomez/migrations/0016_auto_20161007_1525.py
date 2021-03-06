# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-07 14:25
from __future__ import unicode_literals

import datetime
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django_prices.models
import satchless.item


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_smtpsetting_cloud_smtp_configuration'),
        ('gomez', '0015_kitsystem_default_sms_sender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PE', 'Pending'), ('AC', 'Active'), ('CA', 'Cancelled'), ('FR', 'Fraud')], default='PE', max_length=32, verbose_name='order status')),
                ('order_number', models.IntegerField(max_length=10, unique=True)),
                ('ip_address', models.GenericIPAddressField(editable=False, null=True)),
                ('note', models.CharField(blank=True, max_length=255)),
                ('total_net', django_prices.models.PriceField(blank=True, currency='NGN', decimal_places=2, max_digits=12, null=True)),
                ('total_tax', django_prices.models.PriceField(blank=True, currency='NGN', decimal_places=2, max_digits=12, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('last_modified', models.DateTimeField(auto_now_add=True)),
                ('billing_address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.OrganizationContact')),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.KITUser')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gomez.Invoice')),
            ],
            bases=(models.Model, satchless.item.ItemSet),
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999)])),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gomez.Order')),
            ],
            bases=(models.Model, satchless.item.ItemLine),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField()),
                ('price', django_prices.models.PriceField(currency='NGN', decimal_places=2, max_digits=12, verbose_name='Price')),
                ('active', models.BooleanField(default=True)),
                ('paytype', models.CharField(choices=[('RECURRING', 'Recurring'), ('ONETIME', 'One Time')], max_length=20)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            bases=(models.Model, satchless.item.Item),
        ),
        migrations.AddField(
            model_name='kitbilling',
            name='last_renew_date',
            field=models.DateField(default=datetime.datetime(2016, 10, 7, 14, 25, 49, 731407, tzinfo=utc), editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kitserviceplan',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='kitserviceplan',
            name='description',
            field=models.TextField(default='Hello'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kitserviceplan',
            name='email_unit_bundle',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='kitbilling',
            name='billing_cycle',
            field=models.CharField(choices=[('MO', 'Monthly - 1month'), ('QU', 'Quarterly - 3months'), ('BI', 'Biannually - 6months'), ('AN', 'Annually - 1year'), ('BE', 'Biennially - 2years')], default='AN', max_length=2),
        ),
        migrations.AddField(
            model_name='orderline',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='gomez.Product'),
        ),
    ]
