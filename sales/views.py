from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
import json
from django.db import transaction as trans
from .models import Customer, Invoice
from ledger.models import Category, Account
from inventory.models import Item
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic
from . import utils

def customers(request):
	customers = Customer.objects.order_by('id')
	return render(request, 'sales/customers.html', context={"customers": customers})

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
			category = Category.objects.filter(name__iexact='debtors').first()
			account = Account(name=name,account_number=utils.generate_random_number(),category=category)
			account.full_clean()
			account.save()
			customer = Customer(name=name, email=email, phone=phone, address=address, account=account)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)

def invoices(request):
	invoices = Invoice.objects.order_by('id')
	return render(request, 'sales/invoices.html', context={"invoices": invoices})

def invoice_add(request):
	items = [i.select() for i in Item.objects.all()]
	return render(request, 'sales/invoice_add.html', context={'items':items})

def invoice_post(request):
	data = json.loads(request.body)
	name = data['name']
	email = data['email']
	phone = data['phone']
	address = data['address']

	try:
		with trans.atomic():
			category = Category.objects.filter(name__iexact='debtors').first()
			account = Account(name=name,account_number=utils.generate_random_number(),category=category)
			account.full_clean()
			account.save()
			customer = Customer(name=name, email=email, phone=phone, address=address, account=account)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)

def invoice(request,id):
	buffer = utils.generate_invoice(id)
	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
