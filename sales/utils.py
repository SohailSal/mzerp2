import random
from ledger.models import Category, Account, Document
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
from num2words import num2words
from datetime import datetime

def generate_invoice_number(d):
    chunks = []
    document = get_object_or_404(Document, pk=2)
    prefix = document.prefix
    dt = datetime.strptime(d,'%Y-%m-%d')
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    counter = '1' if Invoice.objects.count() == 0 else str(int(Invoice.objects.last().invoice_number.split('/')[-1])+1)
    chunks.append(prefix+'/')
    chunks.append(year+'/')
    chunks.append(month+'/')
    # chunks.append(counter.zfill(3))
    chunks.append(counter)
    str1 = ""
    for ele in chunks:
        str1 += ele
 
    return str1

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

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

	# Define styles
    styles = getSampleStyleSheet()
    heading3 = styles["h3"]
    heading_style = ParagraphStyle(name="Heading", fontSize=12, bold=True)
    subheading_style = ParagraphStyle(name="Subheading", fontSize=12)
    data_style = ParagraphStyle(name="Data", fontSize=10)

    h = 800
    h = h-50
    c.drawString(30, h, company_name)
    c.drawString(300, h, "Bill To:")
    h = h-20
    c.drawString(30, h, company_address)
    c.drawString(300, h, invoice.customer.name)
    h = h-20
    c.drawString(30, h, company_contact)
    c.drawString(300, h, invoice.customer.address)
    h = h-30
    c.drawString(30, h, f"Invoice Number: {invoice.invoice_number}")
    h = h-20
    c.drawString(30, h, f"Invoice Date: {invoice.invoice_date}")

	# Create product table
    data = [[Paragraph("PRODUCT", heading_style), Paragraph("QUANTITY", heading_style), Paragraph("PRICE", heading_style), Paragraph("AMOUNT", heading_style)]]
    data.extend([[Paragraph(p["name"], data_style), Paragraph(str(p["quantity"]), data_style), Paragraph(f"Rs.{p['price']:.2f}", data_style), Paragraph(f"Rs.{p['quantity'] * p['price']:.2f}", data_style)] for p in products])

    table = Table(data, colWidths=[100, 100, 100, 100], style=[('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])

    cnt = len(products)
    th = cnt*20 + 50
    h = h - th
    table.wrapOn(c, 50, h)
    table.drawOn(c, 50, h)

	# Calculate total amount
    total_amount = sum([p["quantity"] * p["price"] for p in products])

	# Add total amount
    h = h - 30
    c.drawString(50, h, "Total Amount:")
    c.drawString(350, h, f"Rs.{total_amount:.2f}")
    h = h - 20
    c.drawString(50, h, "Rupees")
    c.drawString(100, h, num2words(f"{total_amount:.2f}"))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
