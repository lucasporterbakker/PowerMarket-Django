# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-31 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0023_userprofile_linkedin_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='qualified_lead',
            field=models.BooleanField(default=False, verbose_name='qualified lead'),
        ),
    ]
