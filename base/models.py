from django.db import models

class Year(models.Model):
    year = models.IntegerField(unique=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    closed = models.BooleanField(default=False)
    previous = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.year)

class Setting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    def select(self):
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
        }

class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name
