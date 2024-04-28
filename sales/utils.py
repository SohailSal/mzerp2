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
    # d = date.today()
    prefix = document.prefix
    dt = datetime.strptime(d,'%Y-%m-%d')
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    # counter = '1' if Invoice.objects.count() == 0 else str(int(Invoice.objects.last().invoice_number[-3:])+1)
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
    data.extend([[Paragraph(p["name"], normal), Paragraph(str(p["quantity"]), normal), Paragraph(f"Rs.{p['price']:.2f}", data_style), Paragraph(f"{p['discount']}%", data_style), Paragraph(f"Rs.{p['quantity'] * p['price'] * (1 - p['discount']/100):.2f}", data_style)] for p in products])

    table = Table(data, colWidths=[100, 100, 70, 100, 100], style=[('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
    table.wrapOn(c, 50, 520)
    table.drawOn(c, 50, 520)

	# Calculate total amount
    total_amount = sum([p["quantity"] * p["price"] * (1 - p["discount"]/100) for p in products])

	# Add total amount
    c.drawString(50, 370, "Total Amount:")
    c.drawString(450, 370, f"Rs.{total_amount:.2f}")
    c.drawString(50, 350, "Rupees")
    c.drawString(100, 350, num2words(f"{total_amount:.2f}"))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
