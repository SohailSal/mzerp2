from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction as trans
from django.db import DatabaseError 
from .models import Transaction, Document, Account, Entry, Category
from base.models import Setting, Year
from icecream import ic
import fiscalyear
import json
import decimal
from . import utils

# Transactions CRUD
@login_required
def transactions(request):
	transactions = Transaction.objects.order_by('id')
	return render(request, 'ledger/transactions.html', context={"transactions": transactions})

@login_required
def transaction_add(request):
	accounts = [i.select() for i in Account.objects.all()]
	return render(request, 'ledger/transaction_add.html', context={"accounts": accounts})

def transaction_post(request):
	data = json.loads(request.body)
	date = data['date']
	ref = utils.generate_trans_number(date) if data['date'] else None
	description = data['description']
	document = get_object_or_404(Document, pk=1)
	year_setting = Setting.objects.filter(name__iexact='year').first().value
	year = get_object_or_404(Year, pk=year_setting)
	entries = []

	try:
		with trans.atomic():
			transaction = Transaction(ref=ref, date=date, document=document, year=year, description=description)
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

@login_required
def categories(request):
	categories = [i.select() for i in Category.objects.all()]
	return render(request, 'ledger/categories.html', context={"categories": categories})

@login_required
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
	category_number = 1 if parent_category == None or parent_category.category_set.count() == 0 else int(parent_category.category_set.order_by('category_number').last().category_number)+1

	try:
		with trans.atomic():
			category = Category(name=name, level=level, parent_category=parent_category, category_number=category_number)
			category.full_clean()
			category.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	# messages.success(request, 'The category has been saved.')
	# return render(request, 'ledger/categories.html', context={})
	# return HttpResponseRedirect('ledger:categories')
	return JsonResponse({'messages':{'success':'The Category saved!'}}, safe=False)

def category_edit(request,id):
	category = get_object_or_404(Category, pk=id)
	return render(request, 'ledger/category_edit.html', context={"category":category})

def category_edit_post(request):
	category = get_object_or_404(Category, pk=request.POST['id'])
	category.name = request.POST['name']
	category.save()
	messages.success(request, 'The category has been updated successfully.')
	return HttpResponseRedirect(reverse('ledger:categories'))

def category_delete(request,id):
	category = get_object_or_404(Category, pk=id)
	category.delete()
	messages.success(request, 'The category has been deleted successfully.')
	return HttpResponseRedirect(reverse('ledger:categories'))

# Account CRUD

@login_required
def accounts(request):
	accounts = [i.select() for i in Account.objects.filter(customer__isnull=True)]
	return render(request, 'ledger/accounts.html', context={"accounts": accounts})

@login_required
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

def account_edit(request,id):
	account = get_object_or_404(Account, pk=id)
	ac_cat = account.category.id
	categories = utils.tree()
	return render(request, 'ledger/account_edit.html', context={"account":account, "categories": categories, "ac_cat": ac_cat})

def account_edit_post(request):
	account = get_object_or_404(Account, pk=request.POST['id'])
	category = get_object_or_404(Category, pk=request.POST['category'])
	if account.category == category:
		account.name = request.POST['name']
		account.save()
	else:
		account.name = request.POST['name']
		account.category = category
		account.account_number = utils.generate_account_number(category)
		account.save()
	messages.success(request, 'The account has been updated successfully.')
	return HttpResponseRedirect(reverse('ledger:accounts'))

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

def report(request,id):
	account = get_object_or_404(Account, pk=id)
	entries = [i.ledger() for i in Entry.objects.filter(account=account)]
	response = utils.generate_report(entries)
	return response
