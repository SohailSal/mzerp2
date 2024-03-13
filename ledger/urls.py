from django.urls import path
from . import views

app_name = "ledger"
urlpatterns = [
    path("transactions", views.transactions, name="transactions"),
	path('transaction_add',views.transaction_add,name='transaction_add'),
    path('transaction_post', views.transaction_post, name='transaction_post'),
    # path('sample_post', views.sample_post, name='sample_post'),
#    path('edit/<int:id>', views.transaction_edit, name='transaction_edit'),
#    path('transaction_edit_post', views.transaction_edit_post, name='transaction_edit_post'),
    path('transaction_delete/<int:id>', views.transaction_delete, name='transaction_delete'),
    path('report', views.report, name='report'),
]