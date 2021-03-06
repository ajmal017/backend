# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-15 13:00
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20160607_0902'),
    ]

    operations = [
        migrations.CreateModel(
            name='MostPopularFundsData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('data', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
