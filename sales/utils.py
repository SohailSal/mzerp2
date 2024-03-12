import random
from ledger.models import Category, Account
from .models import Invoice
from icecream import ic
from django.http import JsonResponse, HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib import colors

def generate_random_number():
    account_number = ""
    
    # Generate the first digit (1-9)
    first_digit = random.randint(1, 9)
    account_number += str(first_digit)
    
    # Generate the remaining digits (0-9)
    for _ in range(9):
        digit = random.randint(0, 9)
        account_number += str(digit)
    
    return account_number

def generate_account_number(request):
    account_array = []
    category = Category.objects.filter(name__iexact='debtors').first()
    parent_cat = category.parent_category
    current_cat = category
    for i in range(category.level):
        account_array.append(current_cat.category_number.zfill(2))
        current_cat = parent_cat
        parent_cat = current_cat.parent_category
    account_array.append(current_cat.category_number)
    account_array.reverse()
    account_array.append(str(int(category.account_set.order_by('account_number').last().account_number)+1))
    # ic(category.account_set.all())
    str1 = ""
    for ele in account_array:
        str1 += ele
 
    ic(account_array)
    ic(str1)
    return JsonResponse({'message':'fine'})

def generate_invoice(id):
    invoice = get_object_or_404(Invoice, pk=id)
    # ic(invoice)
    # ic(invoice.invoiceitem_set.all())
    products = [i.select() for i in invoice.invoiceitem_set.all()]
    # ic(products)
	# accounts = [i.select() for i in Account.objects.all()]
    company_name = "Muniff Ziauddin & Co."
    company_address = "F/17/3, Executive Centre"
    company_contact = "Phone: xxx-xxx-xxxx, Email: info@mzco.com.pk"
    oldproducts = [
		{"name": "Prod 1", "quantity": 2, "price": 10.00, "discount": 10},
		{"name": "Prod 2", "quantity": 1, "price": 25.00, "discount": 5},
	]

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

	# Define styles
    styles = getSampleStyleSheet()
    normal = styles["h3"]
    heading_style = ParagraphStyle(name="Heading", fontSize=16, bold=True)
    subheading_style = ParagraphStyle(name="Subheading", fontSize=12)
    data_style = ParagraphStyle(name="Data", fontSize=10)

    c.drawString(30, 750, company_name)
    c.drawString(30, 730, company_address)
    c.drawString(30, 710, company_contact)
    c.drawString(300, 750, "Bill To:")
    c.drawString(300, 730, invoice.customer.name)
    c.drawString(300, 710, invoice.customer.address)
    c.drawString(30, 680, f"Invoice Number: {invoice.invoice_number}")
    c.drawString(30, 660, f"Invoice Date: {invoice.invoice_date}")

	# Create product table
    data = [[Paragraph("Product", heading_style), Paragraph("Quantity", heading_style), Paragraph("Price", heading_style), Paragraph("Discount", heading_style), Paragraph("Amount", heading_style)]]
    data.extend([[Paragraph(p["name"], normal), Paragraph(str(p["quantity"]), normal), Paragraph(f"${p['price']:.2f}", data_style), Paragraph(f"{p['discount']}%", data_style), Paragraph(f"${p['quantity'] * p['price'] * (1 - p['discount']/100):.2f}", data_style)] for p in products])

    table = Table(data, colWidths=[100, 100, 70, 100, 100], style=[('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
    table.wrapOn(c, 100, 520)
    table.drawOn(c, 100, 520)


    data2 = [
    ["Letter", "Number", "Stuff", "Long stuff that should be wrapped"],
    ["A", "01", "ABCD", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"],
    ["B", "02", "CDEF", "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"],
    ["C", "03", "SDFSDF", "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"],
    ["D", "04", "SDFSDF", "DDDDDDDDDDDDDDDDDDDDDDDD DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD"],
    ["E", "05", "GHJGHJGHJ", "EEEEEEEEEEEEEE EEEEEEEEEEEEEEEEE EEEEEEEEEEEEEEEEEEEE"],
    ]

    #TODO: Get this line right instead of just copying it from the docs
    style = TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
                        ('TEXTCOLOR',(1,1),(-2,-2),colors.red),
                        ('VALIGN',(0,0),(0,-1),'TOP'),
                        ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                        ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                        ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                        ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                        ])
    s = styles["BodyText"]
    # s.wordWrap = 'CJK'
    # data3 = [data2]
    t=Table(data2)
    # t.setStyle(style)
    t.wrapOn(c, 100, 400)
    t.drawOn(c, 100, 400)


	# Calculate total amount
    total_amount = sum([p["quantity"] * p["price"] * (1 - p["discount"]/100) for p in products])

	# Add total amount
    c.drawString(30, 170, "Total Amount:")
    c.drawString(540, 170, f"${total_amount:.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
