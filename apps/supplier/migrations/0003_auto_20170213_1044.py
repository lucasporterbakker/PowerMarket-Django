# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-13 10:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplier', '0002_auto_20161020_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliercontact',
            name='phone',
            field=models.CharField(default='555-5555-5555', max_length=50),
            preserve_default=False,
        ),
    ]
