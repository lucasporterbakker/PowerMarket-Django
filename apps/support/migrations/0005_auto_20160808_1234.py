# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-08 12:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0004_auto_20160807_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callrequest',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='callrequest',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
