# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-22 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_auto_20160620_0620'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='rebuild_portfolio',
            field=models.BooleanField(default=False),
        ),
    ]