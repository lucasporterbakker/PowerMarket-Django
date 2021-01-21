# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-10 17:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0019_auto_20170410_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electricitybill',
            name='apr',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='aug',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='dec',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='feb',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='jan',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='jul',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='jun',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='mai',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='mar',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='nov',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='oct',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='provider',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='sep',
        ),
        migrations.RemoveField(
            model_name='electricitybill',
            name='year',
        ),
        migrations.AddField(
            model_name='electricitybill',
            name='file',
            field=models.FileField(null=True, upload_to='uploads/electricity_bills/'),
        ),
    ]
