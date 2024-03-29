# Generated by Django 5.0 on 2024-01-26 23:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.company'),
        ),
        migrations.AddField(
            model_name='year',
            name='company',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='base.company'),
            preserve_default=False,
        ),
    ]
