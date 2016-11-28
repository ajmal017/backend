# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-16 10:33
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_auto_20161114_0421'),
         #('core', '0033_auto_20161021_0517'),
       
    ]

    operations = [
        migrations.CreateModel(
            name='LiquidFunds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Modified at')),
                ('number_of_holdings_total', models.BigIntegerField()),
                ('top_ten_holdings', models.FloatField()),
                ('average_maturity', models.FloatField()),
                ('modified_duration', models.FloatField()),
                ('yield_to_maturity', models.FloatField()),
                ('number_of_holdings_top_three_portfolios', django.contrib.postgres.fields.hstore.HStoreField()),
                ('credit_quality_a', models.FloatField()),
                ('credit_quality_aa', models.FloatField()),
                ('credit_quality_aaa', models.FloatField()),
                ('average_credit_quality', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='fund',
            name='image_url',
            field=models.ImageField(blank=True, max_length=700, null=True, upload_to='fund/image/'),
        ),
        migrations.AlterField(
            model_name='fund',
            name='type_of_fund',
            field=models.CharField(choices=[('E', 'Equity'), ('D', 'Debt'), ('T', 'ELSS'), ('L', 'Liquid')], max_length=1),
        ),
        migrations.AlterField(
            model_name='portfolioitem',
            name='broad_category_group',
            field=models.CharField(choices=[('E', 'Equity'), ('D', 'Debt'), ('T', 'ELSS'), ('L', 'Liquid')], max_length=1),
        ),
        migrations.AddField(
            model_name='liquidfunds',
            name='fund',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Fund'),
        ),
    ]