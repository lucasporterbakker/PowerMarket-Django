# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-17 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0007_auto_20160917_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='notes',
            field=models.TextField(blank=True, help_text='project related notes added by user.', null=True, verbose_name='notes'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='title'),
        ),
        migrations.AddField(
            model_name='exampleassessment',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='name'),
        ),
        migrations.AddField(
            model_name='exampleassessment',
            name='published',
            field=models.BooleanField(default=True, help_text='Set to False to hide this example.', verbose_name='published'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='annual_earnings_estimate',
            field=models.FloatField(blank=True, null=True, verbose_name='earnings estimate [£]'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='annual_energy_estimate',
            field=models.FloatField(blank=True, null=True, verbose_name='energy estimate [kWh/year]'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='annual_savings_estimate',
            field=models.FloatField(blank=True, null=True, verbose_name='savings estimate [£]'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='selected_area',
            field=models.FloatField(blank=True, null=True, verbose_name='selected area [sqm]'),
        ),
        migrations.AlterField(
            model_name='exampleassessment',
            name='info',
            field=models.TextField(blank=True, help_text='displayed on the assessment page.', null=True, verbose_name='information'),
        ),
    ]
