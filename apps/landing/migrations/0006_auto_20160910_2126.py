# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-10 21:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0005_auto_20160809_2022'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lexiconentry',
            options={'verbose_name_plural': 'lexicon entries'},
        ),
    ]