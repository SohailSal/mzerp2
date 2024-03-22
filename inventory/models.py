from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    purchase_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    sale_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def select(self):
        return {
            'id': self.id,
            'name': self.name,
        }
