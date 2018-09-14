# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-14 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20180911_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='year',
            field=models.CharField(blank=True, max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='movielink',
            name='episode_nr',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
