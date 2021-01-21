# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-28 22:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0014_auto_20161028_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='manager.Project', verbose_name='project'),
        ),
    ]
