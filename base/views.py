from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Setting, Year
from icecream import ic
import fiscalyear
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime

# settings

def settings(request):
	settings = Setting.objects.all()
	return render(request, 'base/settings.html', context={'settings':settings})

def setting_add(request):
	return render(request, 'base/setting_add.html')

def setting_post(request):
	name = request.POST['name']
	value = request.POST['value']
	setting = Setting(name=name, value=value)
	try:
		setting.full_clean()
		setting.save()
		messages.success(request, 'The setting has been created successfully.')
		return HttpResponseRedirect(reverse('base:settings'))
	except ValidationError as e:
#		messages.error(request, e)
#		return HttpResponseRedirect(reverse('base:settings'))
		return render(request, 'base/setting_add.html', 
			context={"name":request.POST['name'], "value":request.POST['value'],"errors":e}
		)

def setting_edit(request,id):
	setting = get_object_or_404(Setting, pk=id)
	return render(request, 'base/setting_edit.html', context={"setting":setting})

def setting_edit_post(request):
	setting = get_object_or_404(Setting, pk=request.POST['id'])
	setting.name = request.POST['name']
	setting.value = request.POST['value']
	setting.save()
	messages.success(request, 'The setting has been updated successfully.')
	return HttpResponseRedirect(reverse('base:settings'))

def setting_delete(request,id):
	setting = get_object_or_404(Setting, pk=id)
	setting.delete()
	messages.success(request, 'The setting has been deleted successfully.')
	return HttpResponseRedirect(reverse('base:settings'))

# years

def years(request):
	years = Year.objects.all()
	return render(request, 'base/years.html', context={'years':years})

def year_add(request):
	return render(request, 'base/year_add.html')

def year_post(request):
    fiscalyear.setup_fiscal_calendar(start_month=7)
    a = fiscalyear.FiscalYear(int(request.POST['year']))
    # ic(a.start.strftime("%Y-%m-%d, %H:%M:%S"))
    # ic(a.fiscal_year)
    # ic(a.start.month)
    # ic(a.start.year)
    # ic(a.end.month)
    # ic(a.end.year)
    year = Year(year=a.fiscal_year, start_date=a.start.strftime("%Y-%m-%d %H:%M:%S"), end_date=a.end.strftime("%Y-%m-%d %H:%M:%S"))
    try:
        year.full_clean()
        year.save()
        messages.success(request, 'The year has been created successfully.')
        return HttpResponseRedirect(reverse('base:years'))
    except ValidationError as e:
		# ic(e)
		# a = fiscalyear.FiscalYear(2018)
		# fiscalyear.setup_fiscal_calendar(start_month=7)
		# ic(a.start)
		# ic(a.end)
        return render(request, 'base/year_add.html', 
            context={"year":request.POST['year'],"errors":e}
        )

# def year_edit(request,id):
# 	year = get_object_or_404(Year, pk=id)
# 	return render(request, 'base/year_edit.html', context={"year":year})

# def year_edit_post(request):
# 	year = get_object_or_404(Year, pk=request.POST['id'])
# 	year.year = request.POST['year']
# 	year.save()
# 	messages.success(request, 'The year has been updated successfully.')
# 	return HttpResponseRedirect(reverse('base:years'))

def year_delete(request,id):
	year = get_object_or_404(Year, pk=id)
	year.delete()
	messages.success(request, 'The year has been deleted successfully.')
	return HttpResponseRedirect(reverse('base:years'))

# logins

def home(request):
    return render(request, 'base/home.html')
 
@login_required
def dashboard(request):
	users = User.objects.order_by('id')
	return render(request, 'base/dashboard.html', context={"users": users})

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
         
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login')
         
        user = authenticate(username=username, password=password)
         
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login')
        else:
            auth_login(request, user)
            return redirect('/dashboard')
     
    return render(request, 'base/login.html')
 
def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
         
        user = User.objects.filter(username=username)
         
        if user.exists():
            messages.info(request, "Username already taken!")
            return redirect('/register')
         
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username
        )
         
        user.set_password(password)
        user.save()
         
        messages.info(request, "Account created Successfully!")
        return redirect('/register')
     
    return render(request, 'base/register.html')

def logout_view(request):
    logout(request)
    return redirect('/home')