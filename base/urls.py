from django.urls import path,include
from . import views
from . import utils

app_name = "base"
urlpatterns = [
	path('base',views.base,name='base'),
	path('',views.blank,name='blank'),
	path('setting_add',views.setting_add,name='setting_add'),
    path('alpine', views.alpine_form, name='alpine'),
    path('chart', views.chart, name='chart'),
    path('setting_post', views.setting_post, name='setting_post'),
    path('edit/<int:id>', views.setting_edit, name='setting_edit'),
    path('setting_edit_post', views.setting_edit_post, name='setting_edit_post'),
    path('delete/<int:id>', views.setting_delete, name='setting_delete'),
    path('xlsx', utils.xlsx, name='xlsx'),
    path('pdf', utils.pdf, name='pdf'),
    path('invoice', utils.invoice, name='invoice'),
    path('pdf2', utils.pdf2, name='pdf2'),
    path('pdfletter', utils.pdfletter, name='pdfletter'),
    path('pdfmy', utils.pdfmy, name='pdfmy'),
    path('gopdf', utils.gopdf, name='gopdf'),
    path('ledger', utils.ledger, name='ledger'),

# logins
    path('home', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'), 
    path('logout', views.logout_view, name='logout'),    
]