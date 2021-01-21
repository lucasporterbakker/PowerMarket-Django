# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-26 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20160808_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='status',
            field=models.IntegerField(choices=[(0, 'offer requested'), (1, 'contacted by team'), (2, 'offer processing'), (3, 'offer delivered'), (4, 'sale complete')], default=0),
        ),
        migrations.AddField(
            model_name='contact',
            name='test',
            field=models.BooleanField(default=False, help_text='tick this to indicate test contacts.'),
        ),
    ]
