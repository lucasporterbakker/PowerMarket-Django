# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-19 16:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='providerprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='ProviderProfile',
        ),
    ]