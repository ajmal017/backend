# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-31 08:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('external_api', '0002_bankdetails_micr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankdetails',
            name='updated',
            field=models.BooleanField(default=False),
        ),
    ]
