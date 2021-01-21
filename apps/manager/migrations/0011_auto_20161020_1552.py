# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-20 15:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='user.UserProfile'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='supplier.SupplierProfile'),
        ),
    ]