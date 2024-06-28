from django.urls import path,include
from . import views
from . import utils

app_name = "base"
urlpatterns = [
	path('',views.home),
	path('settings',views.settings,name='settings'),
    path('settings_save', views.settings_save, name='settings_save'),
	path('years',views.years,name='years'),
 	path('year_add',views.year_add,name='year_add'),
    path('year_post', views.year_post, name='year_post'),
    path('year_delete/<int:id>', views.year_delete, name='year_delete'),
    path('year_close/<int:id>', views.year_close, name='year_close'),

# logins
    path('home', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'), 
    path('logout', views.logout_view, name='logout'),

# reports
    path('reports', views.reports, name='reports'),  
    path('reports_ledger', views.reports_ledger, name='reports_ledger'),
    path('reports_tb', views.reports_tb, name='reports_tb'),
    path('reports_chart_accounts', views.reports_chart_accounts, name='reports_chart_accounts'),
]