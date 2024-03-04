from django.contrib import admin
from .models import Setting, Year, Tax

admin.site.register(Setting)
admin.site.register(Year)
admin.site.register(Tax)