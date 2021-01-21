# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-04-13 10:14
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True)),
                ('address', models.CharField(max_length=255)),
                ('coords', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('status', models.IntegerField(choices=[(1, 'searched'), (2, 'assessed')], default=1)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_searches', to='location.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostalCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('code', models.CharField(max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='location',
            name='postal_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='location_searches', to='location.PostalCode'),
        ),
    ]
