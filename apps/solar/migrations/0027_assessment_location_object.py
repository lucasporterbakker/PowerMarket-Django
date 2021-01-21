# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-13 12:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20170413_1024'),
        ('solar', '0026_auto_20170410_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='location_object',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='location.Location'),
        ),
    ]
