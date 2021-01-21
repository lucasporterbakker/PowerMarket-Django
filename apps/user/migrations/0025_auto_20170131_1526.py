# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-31 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0024_auto_20170131_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.IntegerField(choices=[(0, 'contact created'), (1, 'contacted by team'), (2, 'offer processing'), (3, 'offer delivered'), (4, 'sale complete'), (5, 'no response'), (6, 'not interested')], default=0),
        ),
    ]
