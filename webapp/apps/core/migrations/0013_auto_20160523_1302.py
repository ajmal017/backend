# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-23 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_fund_analysis'),
    ]

    operations = [
        migrations.AddField(
            model_name='fundhouse',
            name='url1',
            field=models.URLField(blank=True, null=True, verbose_name='OD url'),
        ),
        migrations.AddField(
            model_name='fundhouse',
            name='url2',
            field=models.URLField(blank=True, null=True, verbose_name='KIAM url'),
        ),
    ]
