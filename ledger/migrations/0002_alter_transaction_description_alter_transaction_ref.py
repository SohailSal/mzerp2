# Generated by Django 5.0 on 2024-02-25 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='description',
            field=models.TextField(default=None),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='ref',
            field=models.CharField(default=None, max_length=20),
        ),
    ]
