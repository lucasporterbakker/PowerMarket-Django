# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-08 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0003_auto_20160726_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='solarenergysystem',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='solarenergysystem',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='solarpanel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='solarpanel',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
