# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-17 12:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0006_reportlink'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportlink',
            name='assessment',
        ),
        migrations.DeleteModel(
            name='ReportLink',
        ),
    ]
