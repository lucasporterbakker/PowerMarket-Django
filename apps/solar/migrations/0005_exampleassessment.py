# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-10 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0004_auto_20160808_1234'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('info', models.TextField(blank=True, null=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='solar.Assessment')),
            ],
        ),
    ]
