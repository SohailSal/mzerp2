from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
import json
from django.db import transaction as trans
from .models import Customer
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic

def customers(request):
	return render(request, 'sales/index.html')

def customer_add(request):
	return render(request, 'sales/customer_add.html', context={})

def customer_post(request):
	data = json.loads(request.body)
	name = data['name']
	email = data['email']
	phone = data['phone']
	address = data['address']

	try:
		with trans.atomic():
			customer = Customer(name=name, email=email, phone=phone, address=address)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)
