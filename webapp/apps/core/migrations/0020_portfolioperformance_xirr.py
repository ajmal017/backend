# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-07 07:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_remove_fund_fund_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioperformance',
            name='xirr',
            field=models.FloatField(default=0.0),
        ),
    ]
