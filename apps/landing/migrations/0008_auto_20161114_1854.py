# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-14 18:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0007_pressentry'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lexiconentry',
            options={'ordering': ('term',), 'verbose_name_plural': 'lexicon entries'},
        ),
        migrations.AlterModelOptions(
            name='pressentry',
            options={'ordering': ('-date',), 'verbose_name_plural': 'press entries'},
        ),
    ]
