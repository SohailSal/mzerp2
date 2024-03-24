from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
import json
from django.db import transaction as trans
from .models import Customer, Invoice, InvoiceItem
from ledger.models import Category, Account, Document, Transaction, Entry
from inventory.models import Item
from base.models import Setting
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
	customers = [i.select() for i in Customer.objects.all()]
	return render(request, 'sales/invoice_add.html', context={'items':items,'customers':customers})

def invoice_post(request):
	data = json.loads(request.body)
	invoice_number = data['invoice_number']
	customer = None if (data['customer'] == '') else get_object_or_404(Customer, pk=data['customer'])
	invoice_date = data['invoice_date']
	description = data['description']
	document = get_object_or_404(Document, pk=2)
	items = []
	cab1 = Setting.objects.filter(name__iexact='cab1').first().value
	cs = Setting.objects.filter(name__iexact='cs').first().value
	debit = get_object_or_404(Account, pk=cab1) if (customer == None) else get_object_or_404(Account, pk=customer.id)
	credit = get_object_or_404(Account, pk=cs)
	total = 0

	try:
		with trans.atomic():
			transaction = Transaction(ref=invoice_number, date=invoice_date, document=document, description=description)
			transaction.full_clean()
			transaction.save()
			invoice = Invoice(transaction=transaction, invoice_number=invoice_number, customer=customer, invoice_date=invoice_date, description=description)
			invoice.full_clean()
			invoice.save()
			for entry in data['entries']:
				item = get_object_or_404(Item, pk=entry['item'])
				quantity = float(entry['quantity'])
				rate = float(entry['rate'])
				amount = float(entry['amount'])
				total = total + amount
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

	return JsonResponse({'messages':{'success':'The document saved!'}}, safe=False)

def getRate(request):
	data = json.loads(request.body)
	item = get_object_or_404(Item, pk=data['item'])
	return JsonResponse({'rate': item.sale_rate}, safe=False)

def invoice(request,id):
	buffer = utils.generate_invoice(id)
	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
