from django.urls import path
from . import views

app_name = "inventory"
urlpatterns = [
    path("items", views.items, name="items"),
	path('item_add',views.item_add,name='item_add'),
    path('item_post', views.item_post, name='item_post'),
    path('item_edit/<int:id>', views.item_edit, name='item_edit'),
    path('item_edit_post', views.item_edit_post, name='item_edit_post'),
    path('item_delete/<int:id>', views.item_delete, name='item_delete'),
]