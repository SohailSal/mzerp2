from django.db import models
from ledger.models import Account, Transaction
from inventory.models import Item

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    account = models.OneToOneField(Account, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def select(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Invoice(models.Model):
    transaction = models.OneToOneField(Transaction, null=True, blank=True, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=14, decimal_places=2)
    rate = models.DecimalField(max_digits=14, decimal_places=2)
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    def __str__(self):
        return self.invoice.invoice_number

    def select(self):
        return {
            'name': self.item.name,
            'quantity': float(self.quantity),
            'price': float(self.rate),
            'discount': float(10.0),
        }
