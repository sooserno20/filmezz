# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-31 20:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_movie_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='movielink',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
