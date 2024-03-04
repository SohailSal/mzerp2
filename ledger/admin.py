from django.contrib import admin
from .models import Category, Account, Document, Transaction, Entry

admin.site.register(Category)
admin.site.register(Account)
admin.site.register(Document)
admin.site.register(Transaction)
admin.site.register(Entry)
