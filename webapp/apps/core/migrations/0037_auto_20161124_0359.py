# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-24 03:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_portfolio_liquid_percentage1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='category',
            field=models.CharField(choices=[('R', 'Retirement'), ('T', 'Tax Saving'), ('BP', 'Buy Property'), ('E', 'Higher Education'), ('W', 'Save for Wedding'), ('O', 'Other Events'), ('I', 'Invest'), ('L', 'liquid'), ('AM', 'Auto Mobile'), ('V', 'Vacation'), ('J', 'Jewellery')], max_length=254, verbose_name='Category'),
        ),
    ]
