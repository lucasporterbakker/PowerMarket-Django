# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-28 19:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0011_auto_20160928_1850'),
    ]

    operations = [
        migrations.AddField(
            model_name='exampleassessment',
            name='slug',
            field=models.SlugField(default='change-this'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exampleassessment',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='exampleassessment',
            name='published',
            field=models.BooleanField(default=True, help_text='Set to False to hide this example.'),
        ),
    ]
