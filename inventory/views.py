from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from django.urls import reverse
from django.contrib import messages
import json
from django.db import transaction as trans
from .models import Item
from django.core.exceptions import ValidationError
from django.db import DatabaseError 
from icecream import ic
# from . import utils

def items(request):
	# request.session['current_url'] = 'inventory/index.html'
	# request.session['app'] = 'inventory' 
	items = Item.objects.all()
	return render(request, 'inventory/items.html', context={'items':items})

def item_add(request):
	return render(request, 'inventory/item_add.html', context={})

def item_post(request):
	data = json.loads(request.body)
	name = data['name']
	unit = data['unit']
	description = data['description']
	purchase_rate = data['purchase_rate']
	sale_rate = data['sale_rate']
	quantity = data['quantity']

	try:
		with trans.atomic():
			item = Item(name=name, unit=unit, description=description, purchase_rate=purchase_rate, sale_rate=sale_rate, quantity=quantity)
			item.full_clean()
			item.save()
	except (ValidationError, DatabaseError) as e:
		ic(e)
		return JsonResponse({'errors':e.message_dict}, safe=False)

	return JsonResponse({'messages':{'success':'The item saved!'}}, safe=False)

def item_edit(request,id):
	item = get_object_or_404(Item, pk=id)
	return render(request, 'inventory/item_edit.html', context={"item":item})

def item_edit_post(request):
	item = get_object_or_404(Item, pk=request.POST['id'])
	item.name = request.POST['name']
	item.unit = request.POST['unit']
	item.description = request.POST['description']
	item.purchase_rate = request.POST['purchase_rate']
	item.sale_rate = request.POST['sale_rate']
	item.quantity = request.POST['quantity']
	item.save()
	messages.success(request, 'The item has been updated successfully.')
	return HttpResponseRedirect(reverse('inventory:items'))

def item_delete(request,id):
	item = get_object_or_404(Item, pk=id)
	item.delete()
	messages.success(request, 'The item has been deleted successfully.')
	return HttpResponseRedirect(reverse('inventory:items'))

# def invoice(request,id):
# 	buffer = utils.generate_invoice(id)
# 	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")
