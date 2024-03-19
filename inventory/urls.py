from django.urls import path
from . import views

app_name = "inventory"
urlpatterns = [
    path("items", views.items, name="items"),
	path('item_add',views.item_add,name='item_add'),
    path('item_post', views.item_post, name='item_post'),
]