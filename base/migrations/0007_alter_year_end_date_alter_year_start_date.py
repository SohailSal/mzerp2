# Generated by Django 5.0 on 2024-04-07 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_alter_setting_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='year',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='year',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
