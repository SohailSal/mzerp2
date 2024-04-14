from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
from django.contrib import messages
import json
from django.db import transaction as trans
from .models import Customer, Invoice, InvoiceItem
from ledger.models import Category, Account, Document, Transaction, Entry
from inventory.models import Item
from base.models import Setting, Year
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic
from . import utils
from ledger import utils as ledger_utils

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
			customers = Setting.objects.filter(name__iexact='customers').first().value
			category = get_object_or_404(Category, pk=customers)
			account = Account(name=name,account_number=ledger_utils.generate_account_number(category),category=category)
			account.full_clean()
			account.save()
			customer = Customer(name=name, email=email, phone=phone, address=address, account=account)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)

def customer_delete(request,id):
	customer = get_object_or_404(Customer, pk=id)
	account = get_object_or_404(Account, pk=customer.account.id)
	customer.delete()
	account.delete()
	messages.success(request, 'The customer has been deleted successfully.')
	return HttpResponseRedirect(reverse('sales:customers'))

def invoices(request):
	invoices = Invoice.objects.order_by('id')
	return render(request, 'sales/invoices.html', context={"invoices": invoices})

def invoice_add(request):
	items = [i.select() for i in Item.objects.all()]
	customers = [i.select() for i in Customer.objects.all()]
	return render(request, 'sales/invoice_add.html', context={'items':items,'customers':customers})

def invoice_post(request):
	data = json.loads(request.body)
	# invoice_number = data['invoice_number']
	invoice_date = data['invoice_date'] if data['invoice_date'] else None
	invoice_number = utils.generate_invoice_number(invoice_date) if data['invoice_date'] else None
	customer = None if (data['customer'] == '') else get_object_or_404(Customer, pk=data['customer'])
	description = data['description']
	document = get_object_or_404(Document, pk=2)
	year_setting = Setting.objects.filter(name__iexact='year').first().value
	year = get_object_or_404(Year, pk=year_setting)
	items = []
	cab1 = Setting.objects.filter(name__iexact='cab1').first().value
	cs = Setting.objects.filter(name__iexact='cs').first().value
	debit = get_object_or_404(Account, pk=cab1) if (customer == None) else get_object_or_404(Account, pk=customer.account.id)
	credit = get_object_or_404(Account, pk=cs)
	total = 0

	try:
		with trans.atomic():
			transaction = Transaction(ref=invoice_number, date=invoice_date, document=document, year=year, description=description)
			transaction.full_clean()
			transaction.save()
			invoice = Invoice(transaction=transaction, invoice_number=invoice_number, customer=customer, invoice_date=invoice_date, description=description)
			invoice.full_clean()
			invoice.save()
			for entry in data['entries']:
				item = get_object_or_404(Item, pk=entry['item']) if entry['item'] else None
				quantity = float(entry['quantity']) if entry['quantity'] else None
				rate = float(entry['rate']) if entry['rate'] else None
				amount = float(entry['amount']) if entry['amount'] else None
				total = (total + amount) if amount else None
				items.append(InvoiceItem(invoice=invoice, item=item, quantity=quantity, rate=rate, amount=amount))
			for item in items:
				item.full_clean()
			for item in items:
				item.save()
			entry1 = Entry(transaction=transaction, account=debit, debit=total, credit=0)
			entry2 = Entry(transaction=transaction, account=credit, debit=0, credit=total)
			entry1.full_clean()
			entry1.save()
			entry2.full_clean()
			entry2.save()
			invoice.amount = total
			invoice.save()

	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The invoice saved!'}}, safe=False)

def getRate(request):
	data = json.loads(request.body)
	if data['item']:
		item = get_object_or_404(Item, pk=data['item'])
		return JsonResponse({'rate': item.sale_rate}, safe=False)
	else:
		return JsonResponse({'rate': 0}, safe=False)

def invoice_delete(request,id):
	invoice = get_object_or_404(Invoice, pk=id)
	transaction = get_object_or_404(Transaction, pk=invoice.transaction.id)
	invoice.delete()
	transaction.delete()
	messages.success(request, 'The invoice has been deleted successfully.')
	return HttpResponseRedirect(reverse('sales:invoices'))

def invoice(request,id):
	buffer = utils.generate_invoice(id)
	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
