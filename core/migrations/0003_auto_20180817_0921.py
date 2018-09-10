# Generated by Django 2.1 on 2018-08-17 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20180816_2212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='image',
        ),
        migrations.AddField(
            model_name='movie',
            name='image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]