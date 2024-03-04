# Generated by Django 5.0 on 2024-02-12 10:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('prefix', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('level', models.PositiveSmallIntegerField()),
                ('parent_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ledger.category')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('account_number', models.CharField(max_length=20, unique=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ledger.category')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('ref', models.CharField(max_length=20)),
                ('description', models.TextField()),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ledger.document')),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('credit', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ledger.account')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ledger.transaction')),
            ],
        ),
    ]
