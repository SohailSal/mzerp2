from django.urls import path
from . import views
from . import utils

app_name = "ledger"
urlpatterns = [
    path("transactions", views.transactions, name="transactions"),
	path('transaction_add',views.transaction_add,name='transaction_add'),
    path('transaction_post', views.transaction_post, name='transaction_post'),
    path('transaction_delete/<int:id>', views.transaction_delete, name='transaction_delete'),
    path("categories", views.categories, name="categories"),
	path('category_add',views.category_add,name='category_add'),
    path('category_post', views.category_post, name='category_post'),
    path('category_edit/<int:id>', views.category_edit, name='category_edit'),
    path('category_edit_post', views.category_edit_post, name='category_edit_post'),
    path('category_delete/<int:id>', views.category_delete, name='category_delete'),
    path("accounts", views.accounts, name="accounts"),
	path('account_add',views.account_add,name='account_add'),
    path('account_post', views.account_post, name='account_post'),
    path('account_edit/<int:id>', views.account_edit, name='account_edit'),
    path('account_edit_post', views.account_edit_post, name='account_edit_post'),
    path('account_delete/<int:id>', views.account_delete, name='account_delete'),
    path('report/<int:id>', views.report, name='report'),
]