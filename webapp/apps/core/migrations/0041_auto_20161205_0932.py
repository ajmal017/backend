# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-05 09:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolioitem',
            name='xsip_reg_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='portfolioitem',
            name='xsip_reg_no',
            field=models.CharField(blank=True, max_length=100, null=True),
        )
    ]
