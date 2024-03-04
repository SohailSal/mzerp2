from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse

def customers(request):
	return render(request, 'sales/index.html')
