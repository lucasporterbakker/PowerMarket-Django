# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-12 17:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0008_auto_20161114_1854'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pressentry',
            old_name='description',
            new_name='headline',
        ),
    ]