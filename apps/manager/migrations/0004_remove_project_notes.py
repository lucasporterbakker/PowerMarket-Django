# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-29 18:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20160928_1846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='notes',
        ),
    ]
