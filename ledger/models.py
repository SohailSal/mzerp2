from django.db import models
from base.models import Year

class Category(models.Model):
    name = models.CharField(max_length=255)
    category_number = models.CharField(max_length=20, null=True, blank=True)
    level = models.PositiveSmallIntegerField()
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def select(self):
        return {
            'id': self.id,
            'name': self.name,
            'parent': self.parent_category,
        }

class Account(models.Model):
    name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def select(self):
        return {
            'id': self.id,
            'name': self.name,
            'account_number': self.account_number,
            'category': self.category.name,
        }

class Document(models.Model):
    name = models.CharField(max_length=255)
    prefix = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    date = models.DateField()
    ref = models.CharField(max_length=20, blank=False, default=None)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    description = models.TextField(blank=False, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ref

class Entry(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Entry {self.id}"

    def ledger(self):
        return {
            'date': self.transaction.date,
            'ref': self.transaction.ref,
            'description': self.transaction.description,
            'debit': float(self.debit),
            'credit': float(self.credit),
        }
