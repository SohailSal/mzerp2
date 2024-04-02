# Generated by Django 5.0 on 2024-03-31 08:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0006_remove_category_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='parent_category',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='ledger.category'),
            preserve_default=False,
        ),
    ]