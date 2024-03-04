from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Setting
from icecream import ic
import fiscalyear
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def base(request):
	return render(request, 'base/base.html')

def blank(request):
	settings = Setting.objects.order_by('id')
	return render(request, 'base/index.html', context={"settings": settings,"hello": "world"})

def setting_add(request):
	return render(request, 'base/setting_add.html')

def alpine_form(request):
    return render(request, 'base/alpine_form.html', context={})

def chart(request):
    return render(request, 'base/chart.html', context={})

def setting_post(request):
	name = request.POST['name']
	value = request.POST['value']
	setting = Setting(name=name, value=value)
	try:
		setting.full_clean()
		setting.save()
		messages.success(request, 'The setting has been created successfully.')
		return HttpResponseRedirect(reverse('base:blank'))
	except ValidationError as e:
		ic(e)
		a = fiscalyear.FiscalYear(2018)
		fiscalyear.setup_fiscal_calendar(start_month=7)
		ic(a.start)
		ic(a.end)
#		messages.error(request, e)
#		return HttpResponseRedirect(reverse('base:blank'))
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
	return HttpResponseRedirect(reverse('base:blank'))

def setting_delete(request,id):
	setting = get_object_or_404(Setting, pk=id)
	setting.delete()
	messages.success(request, 'The setting has been deleted successfully.')
	return HttpResponseRedirect(reverse('base:blank'))

def setting_post_old(request):
    data = request.POST
    print(f'{data = }')

    return JsonResponse({'status': 'success'})

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