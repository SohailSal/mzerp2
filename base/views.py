from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Setting, Year
from .utils import close
from ledger.models import Category, Account, Entry
from icecream import ic
import fiscalyear
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime
from ledger import utils

# settings

@login_required
def settings(request):
    settings = [i.select() for i in Setting.objects.all()]
    accounts = [i.select() for i in Account.objects.all()]
    categories = utils.tree()
    years = Year.objects.all()
    return render(request, 'base/settings.html', context={'settings':settings, 'accounts':accounts, 'categories':categories, 'years':years})

def settings_save(request):
    arr = []
    arr.append(int(request.POST['cab1']))
    arr.append(int(request.POST['cs']))
    arr.append(int(request.POST['customers']))
    arr.append(int(request.POST['year']))
    arr.append(int(request.POST['suspense']))
    settings = Setting.objects.all()
    counter = 0
    for setting in settings:
        setting.value = arr[counter]
        setting.save()
        counter = counter + 1
    messages.success(request, 'The settings have been updated.')
    return HttpResponseRedirect(reverse('base:settings'))
    # return render(request, 'base/dashboard.html')

# years

@login_required
def years(request):
	years = Year.objects.all()
	return render(request, 'base/years.html', context={'years':years})

@login_required
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

def year_close(request,id):
    year = get_object_or_404(Year, pk=id)
    str1 = close(year)
    ic(str1)
    messages.success(request, 'The year has been closed successfully.')
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
            next_url = request.GET.get("next")
            if next_url:
                 return redirect(next_url)
            else:
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

@login_required
def reports(request):
    accounts = [i.select() for i in Account.objects.all()]
    year_setting = Setting.objects.filter(name__iexact='year').first().value
    year = get_object_or_404(Year, pk=year_setting)
    start_date = year.start_date.strftime("%Y-%m-%d")
    end_date = year.end_date.strftime("%Y-%m-%d")
    return render(request, 'base/reports.html', context={"accounts": accounts, "start_date":start_date, "end_date":end_date})

def reports_ledger(request):
    start = request.POST['start_date']
    end = request.POST['end_date']
    account = get_object_or_404(Account, pk=request.POST['acc'])
    entries = [i.ledger() for i in Entry.objects.filter(account=account, transaction__date__range=(start,end))]
    if entries:
        response = utils.generate_report(entries)
        return response
    else:
        messages.warning(request, "No entries were present!")
        return redirect('/reports')

def reports_tb(request):
    dt = request.POST['end_date']
    response = utils.generate_tb(dt)
    return response

def reports_chart_accounts(request):
    response = utils.generate_chart_accounts()
    return response
