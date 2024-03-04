from django.http import HttpResponse, FileResponse
import io
import time
import xlsxwriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from .models import Setting

def xlsx(request):
	output = io.BytesIO()
	wb = xlsxwriter.Workbook(output)
	ws = wb.add_worksheet('one')
#	ws.write('A1','Hello World')

	bold = wb.add_format({'bold': True})
	settings = Setting.objects.all()
	row = 1
	col = 0
	for setting in settings:
		ws.write(row, col, setting.id)
		ws.write(row, col + 1, setting.name)
		ws.write(row, col + 2, setting.value)
		row += 1
	ws.write('B1', 'Name', bold)
	ws.write('C1', 'Value', bold)

	wb.close()
	output.seek(0)
	filename = "django_simple.xlsx"
	response = HttpResponse(
		output,
		content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	)
	response["Content-Disposition"] = "attachment; filename=%s" % filename
	return response

def pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 300, "Hello world.")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")

def invoice(request):

	company_name = "Your Company Name"
	company_address = "Your Company Address"
	company_contact = "Phone: xxx-xxx-xxxx, Email: your_email@example.com"
	client_name = "Client Name"
	client_address = "Client Address"
	invoice_number = "INV1234"
	invoice_date = "2024-02-09"
	products = [
		{"name": "Product 1", "quantity": 2, "price": 10.00, "discount": 10},
		{"name": "Product 2", "quantity": 1, "price": 25.00, "discount": 5},
	]

	buffer = io.BytesIO()
	c = canvas.Canvas(buffer, pagesize=letter)

	# Define styles
	styles = getSampleStyleSheet()
	normal = styles["h1"]
	heading_style = ParagraphStyle(name="Heading", fontSize=16, bold=True)
	subheading_style = ParagraphStyle(name="Subheading", fontSize=12)
	data_style = ParagraphStyle(name="Data", fontSize=10)

	c.drawString(30, 750, company_name)
	c.drawString(30, 730, company_address)
	c.drawString(30, 710, company_contact)
	c.drawString(400, 750, "Bill To:")
	c.drawString(400, 730, client_name)
	c.drawString(400, 710, client_address)
	c.drawString(30, 680, f"Invoice Number: {invoice_number}")
	c.drawString(30, 660, f"Invoice Date: {invoice_date}")

	# Create product table
	data = [[Paragraph("Product", heading_style), Paragraph("Quantity", heading_style), Paragraph("Price", heading_style), Paragraph("Discount", heading_style), Paragraph("Amount", heading_style)]]
	data.extend([[Paragraph(p["name"], normal), Paragraph(str(p["quantity"]), normal), Paragraph(f"${p['price']:.2f}", data_style), Paragraph(f"{p['discount']}%", data_style), Paragraph(f"${p['quantity'] * p['price'] * (1 - p['discount']/100):.2f}", data_style)] for p in products])

	table = Table(data, colWidths=[100, 100, 70, 100, 100], style=[('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')])
	table.wrapOn(c, 100, 520)
	table.drawOn(c, 100, 520)

	# Calculate total amount
	total_amount = sum([p["quantity"] * p["price"] * (1 - p["discount"]/100) for p in products])

	# Add total amount
	c.drawString(30, 370, "Total Amount:")
	c.drawString(440, 370, f"${total_amount:.2f}")

	c.showPage()
	c.save()
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename="invoice.pdf")

def pdf2(request):
	c = canvas.Canvas("form.pdf", pagesize=letter)
	c.setLineWidth(.3)
	c.setFont('Helvetica', 12)
	c.drawString(30,750,'OFFICIAL COMMUNIQUE')
	c.drawString(30,735,'OF GOOD LUCK INDUSTRIES LTD')
	c.drawString(500,750,"01/01/2024")
	c.line(480,747,580,747)
	c.drawString(275,725,'AMOUNT OWED:')
	c.drawString(500,725,"Rs. 1,000.00")
	c.line(378,723,580,723)
	c.drawString(30,703,'RECEIVED BY:')
	c.line(120,700,580,700)
	c.drawString(120,703,"Sohail Bhai")
	c.save()
	return HttpResponse('hello pdf2...see home folder')


def pdfletter(request):

	doc = SimpleDocTemplate("form_letter.pdf",pagesize=letter,
							rightMargin=72,leftMargin=72,
							topMargin=72,bottomMargin=18)
	Story=[]
#	logo = "python_logo.png"
	magName = "Pythonista"
	issueNum = 12
	subPrice = "99.00"
	limitedDate = "03/05/2010"
	freeGift = "tin foil hat"

	formatted_time = time.ctime()
	full_name = "Mike Driscoll"
	address_parts = ["411 State St.", "Marshalltown, IA 50158"]

#	im = Image(logo, 2*inch, 2*inch)
#	Story.append(im)

	styles=getSampleStyleSheet()
	styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
	ptext = '%s' % formatted_time

	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))

	# Create return address
	ptext = '%s' % full_name
	Story.append(Paragraph(ptext, styles["Normal"]))       
	for part in address_parts:
		ptext = '%s' % part.strip()
		Story.append(Paragraph(ptext, styles["Normal"]))   

	Story.append(Spacer(1, 12))
	ptext = 'Dear %s:' % full_name.split()[0].strip()
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))

	ptext = 'We would like to welcome you to our subscriber base for %s Magazine! \
			You will receive %s issues at the excellent introductory price of $%s. Please respond by\
			%s to start receiving your subscription and get the following free gift: %s.' % (magName, 
																									issueNum,
																									subPrice,
																									limitedDate,
																									freeGift)
	Story.append(Paragraph(ptext, styles["Justify"]))
	Story.append(Spacer(1, 12))


	ptext = 'Thank you very much and we look forward to serving you.'
	Story.append(Paragraph(ptext, styles["Justify"]))
	Story.append(Spacer(1, 12))
	ptext = 'Sincerely,'
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 48))
	ptext = 'Sohail Saleem'
	Story.append(Paragraph(ptext, styles["Normal"]))
	Story.append(Spacer(1, 12))
	doc.build(Story)
	return HttpResponse('pdfletter generated...see home folder')

# from official documentation

def pdfmy(request):
	styles = getSampleStyleSheet()
	styleN = styles['Normal']
	styleH = styles['Heading1']
	story = []

	#add some flowables
	story.append(Paragraph("This is a Heading",styleH))
	story.append(Paragraph("This is a paragraph in <i>Normal</i> style.",
		styleN))
	doc = SimpleDocTemplate('mydoc.pdf',pagesize = letter)
	doc.build(story)
	return HttpResponse('mypdf generated...see home folder')

# multipage, canvas alongwith doctemplate

Title = "Hello world"
pageinfo = "platypus example"
PAGE_HEIGHT=defaultPageSize[1]; PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

def myFirstPage(canv, doc):
	canv.saveState()
	canv.setFont('Times-Bold',16)
	canv.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
	canv.setFont('Times-Roman',9)
	canv.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
	canv.restoreState()

def myLaterPages(canv, doc):
	canv.saveState()
	canv.setFont('Times-Roman',9)
	canv.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
	canv.restoreState()

def gopdf(request):
	doc = SimpleDocTemplate("phello.pdf")
	Story = [Spacer(1,2*inch)]
	style = styles["Normal"]
	for i in range(100):
		bogustext = ("This is Paragraph number %s. " % i) *20
		p = Paragraph(bogustext, style)
		Story.append(p)
		Story.append(Spacer(1,0.2*inch))
	doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
	return HttpResponse('gopdf generated...see home folder')

# ledger

data = [
    {"date": "2021-01-01", "description": "Sales", "debit": 1000, "credit": 0},
    {"date": "2021-01-02", "description": "Rent", "debit": 0, "credit": 500},
    {"date": "2021-01-03", "description": "Salary", "debit": 1000, "credit": 0},
    {"date": "2021-01-04", "description": "Utilities", "debit": 0, "credit": 200},
]
def ledger(request):
    c = canvas.Canvas("ledger.pdf")
    c.setFont("Helvetica", 12)
    x = 50
    y = 700
    headers = ["Date", "Description", "Debit", "Credit", "Running Balance"]
    for header in headers:
        c.drawString(x, y, header)
        x += 100
    y -= 20
    running_balance = 0
    for entry in data:
        date = entry["date"]
        description = entry["description"]
        debit = entry["debit"]
        credit = entry["credit"]

        running_balance += debit - credit

        x = 50

        c.drawString(x, y, str(date))
        x += 100
        c.drawString(x, y, description)
        x += 100
        c.drawString(x, y, str(debit))
        x += 100
        c.drawString(x, y, str(credit))
        x += 100
        c.drawString(x, y, str(running_balance))

        y -= 20
    c.showPage()
    c.save()
    return HttpResponse("PDF Ledger generated in parent directory")