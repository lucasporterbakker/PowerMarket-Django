# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-12 12:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0021_auto_20161229_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='nrel_station_distance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='nrel_version',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]