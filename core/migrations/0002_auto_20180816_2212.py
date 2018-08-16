# Generated by Django 2.1 on 2018-08-16 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movielink',
            name='link',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='movielink',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Movie'),
        ),
    ]
