# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-09-03 11:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
        ('core', '0019_auto_20160903_1134'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('address_1', models.CharField(max_length=100, null=True)),
                ('address_2', models.CharField(blank=True, max_length=100, null=True)),
                ('city_town', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cities_light.City')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cities_light.Country')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cities_light.Region')),
            ],
        ),
        migrations.RemoveField(
            model_name='kituser',
            name='address_1',
        ),
        migrations.RemoveField(
            model_name='kituser',
            name='address_2',
        ),
        migrations.RemoveField(
            model_name='kituser',
            name='city_town',
        ),
        migrations.RemoveField(
            model_name='kituser',
            name='state',
        ),
        migrations.AlterField(
            model_name='kituser',
            name='industry',
            field=models.CharField(choices=[('AVIATION', 'Aviation'), ('ENTERTAINMENT', 'Entertainment'), ('RELIGIOUS', 'Religious'), ('FIN_BANK', 'Finance & Banking'), ('EDUCATION', 'Education'), ('MARKETING', 'Marketing'), ('GOVERNMENT', 'Government'), ('OIL_ENERGY', 'Oil & Energy'), ('NGO', 'NGO'), ('IT', 'Information Technology'), ('RETAIL', 'Retail'), ('TRANSPORT_HAULAGE', 'Transportation & Haulage'), ('OTHER', 'Other')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='kituser',
            name='address',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Address'),
        ),
    ]