# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-13 13:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location', '0002_auto_20170413_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='status',
        ),
    ]
