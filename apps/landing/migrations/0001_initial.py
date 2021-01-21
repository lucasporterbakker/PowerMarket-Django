# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-06 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlossaryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=255, verbose_name='term')),
                ('abbreviation', models.CharField(blank=True, max_length=20, null=True, verbose_name='abbreviation')),
                ('description', models.TextField(verbose_name='description')),
            ],
            options={
                'verbose_name_plural': 'glossary entries',
            },
        ),
    ]