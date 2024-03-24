from django.urls import path
from . import views
from . import utils

app_name = "sales"
urlpatterns = [
    path("customers", views.customers, name="customers"),
	path('customer_add',views.customer_add,name='customer_add'),
    path('customer_post', views.customer_post, name='customer_post'),
    path("invoices", views.invoices, name="invoices"),
	path('invoice_add',views.invoice_add,name='invoice_add'),
    path('invoice_post', views.invoice_post, name='invoice_post'),
    path('getRate', views.getRate, name='getRate'),
    path('generate', utils.generate_account_number, name='generate'),
    # path('invoice', utils.invoice, name='invoice'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
]