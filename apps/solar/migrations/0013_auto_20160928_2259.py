# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-28 22:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0012_auto_20160928_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='exampleassessment',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='exampleassessment',
            name='info',
            field=models.TextField(blank=True, help_text='displayed on the assessment page.', null=True),
        ),
    ]
