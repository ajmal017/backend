# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-28 08:41
from __future__ import unicode_literals

from django.db import migrations, models
import profiles.models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_auto_20160901_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fatca_filed',
            field=models.BooleanField(default=False),
        ),
    ]
