from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
import json
from django.db import transaction as trans
from .models import Item
from ledger.models import Category, Account
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic
# from . import utils

def index(request):
	items = Item.objects.all()
	return render(request, 'inventory/index.html', context={'items':items})

def item_add(request):
	return render(request, 'inventory/item_add.html', context={})

def item_post(request):
	data = json.loads(request.body)
	name = data['name']
	email = data['email']
	phone = data['phone']
	address = data['address']

	try:
		with trans.atomic():
			customer = Item(name=name, email=email, phone=phone, address=address)
			customer.full_clean()
			customer.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The customer saved!'}}, safe=False)

# def invoice(request,id):
# 	buffer = utils.generate_invoice(id)
# 	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
