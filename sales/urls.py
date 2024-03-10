from django.urls import path
from . import views
from . import utils

app_name = "sales"
urlpatterns = [
    path("customers", views.customers, name="customers"),
	path('customer_add',views.customer_add,name='customer_add'),
    path('customer_post', views.customer_post, name='customer_post'),
    path('generate', utils.generate_account_number, name='generate'),
    # path('invoice', utils.invoice, name='invoice'),
    path('invoice/<int:id>', views.invoice, name='invoice'),
]