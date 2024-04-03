from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction as trans
from django.db import DatabaseError 
from .models import Transaction, Document, Account, Entry, Category
from icecream import ic
import fiscalyear
import json
import decimal
from . import utils

# Transactions CRUD

def transactions(request):
	transactions = Transaction.objects.order_by('id')
	return render(request, 'ledger/transactions.html', context={"transactions": transactions})

def transaction_add(request):
	accounts = [i.select() for i in Account.objects.all()]
	return render(request, 'ledger/transaction_add.html', context={"accounts": accounts})

def transaction_post(request):
	data = json.loads(request.body)
	ref = data['ref']
	date = data['date']
	description = data['description']
	document = get_object_or_404(Document, pk=1)
	entries = []

	try:
		with trans.atomic():
			transaction = Transaction(ref=ref, date=date, document=document, description=description)
			transaction.full_clean()
			transaction.save()
			for entry in data['entries']:
				account = get_object_or_404(Account, pk=entry['account'])
				debit = 0 if (entry['debit'] == '') else float(entry['debit'])
				credit = 0 if (entry['credit'] == '') else float(entry['credit'])
				entries.append(Entry(transaction=transaction, account=account, debit=debit, credit=credit))
			for entry in entries:
				entry.full_clean()
			for entry in entries:
				entry.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The document saved!'}}, safe=False)

def transaction_delete(request,id):
	trans = get_object_or_404(Transaction, pk=id)
	trans.delete()
	messages.success(request, 'The transaction has been deleted successfully.')
	return HttpResponseRedirect(reverse('ledger:transactions'))

# Category CRUD

def categories(request):
	categories = [i.select() for i in Category.objects.all()]
	return render(request, 'ledger/categories.html', context={"categories": categories})

def category_add(request):
	categories = utils.tree()
	cat = utils.tree2()
	ic(cat)
	return render(request, 'ledger/category_add.html', context={"categories": categories})

def category_post(request):
	data = json.loads(request.body)
	name = data['name'] if data['name'] else None
	parent_category = get_object_or_404(Category, pk=data['parent_category']) if data['parent_category'] else None 
	level = parent_category.level + 1

	try:
		with trans.atomic():
			category = Category(name=name, level=level, parent_category=parent_category)
			category.full_clean()
			category.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	# messages.success(request, 'The category has been saved.')
	# return render(request, 'ledger/categories.html', context={})
	# return HttpResponseRedirect('ledger:categories')
	return JsonResponse({'messages':{'success':'The Category saved!'}}, safe=False)

def category_delete(request,id):
	category = get_object_or_404(Category, pk=id)
	category.delete()
	messages.success(request, 'The category has been deleted successfully.')
	return HttpResponseRedirect(reverse('ledger:categories'))

# Account CRUD

def accounts(request):
	accounts = [i.select() for i in Account.objects.all()]
	return render(request, 'ledger/accounts.html', context={"accounts": accounts})

def account_add(request):
	categories = utils.tree()
	return render(request, 'ledger/account_add.html', context={"categories": categories})

def account_post(request):
	data = json.loads(request.body)
	name = data['name'] if data['name'] else None
	category = get_object_or_404(Category, pk=data['category']) if data['category'] else None 
	balance = data['balance'] if data['balance'] else None
	account_number = utils.generate_account_number(category)

	try:
		with trans.atomic():
			account = Account(name=name, account_number=account_number, category=category, balance=balance)
			account.full_clean()
			account.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The Account saved!'}}, safe=False)

def account_delete(request,id):
	account = get_object_or_404(Account, pk=id)
	account.delete()
	messages.success(request, 'The account has been deleted successfully.')
	return HttpResponseRedirect(reverse('ledger:accounts'))


# def sample_post(request):
#     data = json.loads(request.body)
#     print(data['hello'])
#     print(data['entries'])
#     for x in data['entries']:
#     	print(x['account'])
#     return JsonResponse({'status': 'success'})

def report(request):
	entries = [i.ledger() for i in Entry.objects.all()]
	ic(entries)
	response = utils.generate_report(entries)
	return response