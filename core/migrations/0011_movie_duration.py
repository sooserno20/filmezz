# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-25 17:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20181011_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='duration',
            field=models.PositiveSmallIntegerField(null=True),
        ),
    ]
