# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-06 22:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0003_auto_20160806_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glossaryentry',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='description'),
        ),
    ]
