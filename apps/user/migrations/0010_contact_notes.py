# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-14 18:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_auto_20161010_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='notes',
            field=models.TextField(blank=True, help_text='Add notes here about he correspondence with the contact.', null=True),
        ),
    ]
