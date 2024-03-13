# Generated by Django 5.0 on 2024-03-13 17:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0005_remove_entry_created_at_remove_entry_updated_at'),
        ('sales', '0003_invoice_created_at_invoice_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ledger.transaction'),
        ),
    ]
