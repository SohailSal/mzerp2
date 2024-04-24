from django.urls import path
from . import views
from . import utils

app_name = "sales"
urlpatterns = [
    path("customers", views.customers, name="customers"),
	path('customer_add',views.customer_add,name='customer_add'),
    path('customer_post', views.customer_post, name='customer_post'),
    path('customer_edit/<int:id>', views.customer_edit, name='customer_edit'),
    path('customer_edit_post', views.customer_edit_post, name='customer_edit_post'),
    path('customer_delete/<int:id>', views.customer_delete, name='customer_delete'),
    path("invoices", views.invoices, name="invoices"),
	path('invoice_add',views.invoice_add,name='invoice_add'),
    path('invoice_post', views.invoice_post, name='invoice_post'),
    path('invoice_delete/<int:id>', views.invoice_delete, name='invoice_delete'),
    path('getRate', views.getRate, name='getRate'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
]