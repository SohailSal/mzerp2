import xlsxwriter
import io
from django.db.models import Sum, Q, F
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Category, Transaction, Document, Account, Entry, Closing
from base.models import Setting, Year
from icecream import ic
from datetime import datetime

def generate_report(ledger_data, account):
    # Create a new workbook and add a worksheet
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('ledger')
    header1 = "&CHere is some centered header."
    footer1 = "&LHere is some left aligned footer."

    worksheet.set_header(header1)
    worksheet.set_footer(footer1)
    # Define the column headers
    headers = ['Date', 'Ref', 'Description', 'Debit', 'Credit', 'Running Balance']

    # Write the column headers to the worksheet
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    balance = 0
    ob = 0
    row_count = 3

    format1 = workbook.add_format({'num_format': 'd mmmm yyyy'})
    format2 = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_column(0, 0, 18)

    year_setting = Setting.objects.filter(name__iexact='year').first().value
    year = get_object_or_404(Year, pk=year_setting)
    prev_yr = Year.objects.filter(id = year.previous).first()
    # start_dt = year.start_date.strftime("%Y-%m-%d")

    if (prev_yr) and (prev_yr.closed):
        bal = Closing.objects.filter(year = prev_yr, account = account, pre = 0).last() 
        ob = bal.amount if bal else 0

    worksheet.write(1,2, 'Opening Balance')
    worksheet.write(1,5, ob, format2)
    balance = float(ob)
    for row, data in enumerate(ledger_data, start=2):
        balance += float(data['debit']) - float(data['credit'])

        worksheet.write(row, 0, data['date'], format1)
        worksheet.write(row, 1, data['ref'])
        worksheet.write(row, 2, data['description'])
        worksheet.write(row, 3, data['debit'], format2)
        worksheet.write(row, 4, data['credit'], format2)
        worksheet.write(row, 5, balance, format2)

        row_count = row_count + 1

    # Write the totals
    total_debit = sum(float(data['debit']) for data in ledger_data)
    total_credit = sum(float(data['credit']) for data in ledger_data)

    worksheet.write(row_count, 1, 'Totals')
    worksheet.write(row_count, 3, total_debit, format2)
    worksheet.write(row_count, 4, total_credit, format2)

    # Save the workbook
    worksheet.autofit()
    workbook.close()
    output.seek(0)
    filename = "ledger.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response

def generate_tb(dt):

    # Create a new Excel workbook and add a worksheet
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('tb')

    # Define cell formats
    bold_format = workbook.add_format({'bold': True})
    currency_format = workbook.add_format({'num_format': '#,##0.00'})

    # Write the headers
    worksheet.write('A1', 'Category', bold_format)
    worksheet.write('B1', 'Account', bold_format)
    worksheet.write('C1', 'Debit', bold_format)
    worksheet.write('D1', 'Credit', bold_format)

    year_setting = Setting.objects.filter(name__iexact='year').first().value
    year = get_object_or_404(Year, pk=year_setting)
    start_dt = year.start_date.strftime("%Y-%m-%d")
    # ic(start_dt)
    # ic(dt)

    # Retrieve account balances using Django's aggregation

    account_balances = Account.objects.filter(
        entry__transaction__date__range=(start_dt, dt)
    ).annotate(
        amount=Sum('entry__debit') - Sum('entry__credit'),
        acc = F('id')
    ).values('id','acc','name', 'amount', 'category')

    closings = Closing.objects.filter(year = year.previous).filter(pre = 0).filter(
        Q(account__account_number__startswith='1') | Q(account__account_number__startswith='2') | Q(account__account_number__startswith='3')
    ).annotate(
        name = F('account__name'),
        acc = F('account'),
        category = F('account__category__id')
    ).values('name','acc','account', 'amount', 'category')
    # ic(closings)
    uncommon_openings = closings.exclude(account__in=account_balances.values('id')).values('acc','name','amount','category')
    uncommon_new = account_balances.exclude(id__in=closings.values('account')).values('acc','name','amount','category')

    merged_data = []

    for data1 in account_balances:
        for data2 in closings:
            if data1['id'] == data2['account']:
                merged_data.append({
                    'acc': data1['id'],
                    'name': data1['name'],
                    'amount': data1['amount'] + data2['amount'],
                    'category': data1['category']
                })

    trial_balance = merged_data + list(uncommon_openings) + list(uncommon_new)

    categories = tree()

    row = 1
    total_debit = 0
    total_credit = 0
    for category in categories:
        # ic(category["id"])
        # cat = get_object_or_404(Category, pk=category["id"])
        # accounts = account_balances.filter(category=cat)

        accounts = [ i for i in trial_balance if i['category'] == category['id']]

        row += 1
        worksheet.write(row, 0, category["name"])
    # row = 1
        for account in accounts:
            worksheet.write(row, 1, account['name'])
            if account['amount'] >= 0:
                worksheet.write(row, 2, account['amount'], currency_format)
                total_debit = total_debit + account['amount']
            else:
                worksheet.write(row, 3, abs(account['amount']), currency_format)
                total_credit = total_credit + abs(account['amount'])
            # worksheet.write(row, 2, account['category'])
            # worksheet.write(row, 3, account['id'])
            row += 1

    worksheet.write(row + 2, 1, 'Totals')
    worksheet.write(row + 2, 2, total_debit, currency_format)
    worksheet.write(row + 2, 3, total_credit, currency_format)


    worksheet.autofit()
    workbook.close()
    output.seek(0)
    filename = "tb.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response

def generate_chart_accounts():
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('coa')

    bold_format = workbook.add_format({'bold': True})

    worksheet.write('A1', 'Category', bold_format)
    worksheet.write('B1', 'Number', bold_format)
    worksheet.write('C1', 'Account', bold_format)

    categories = tree()

    row = 1
    for category in categories:
        cat = get_object_or_404(Category, pk=category["id"])
        accounts = Account.objects.filter(category=cat)
        row += 1
        worksheet.write(row, 0, category["name"])
        for account in accounts:
            worksheet.write(row, 1, account.account_number)
            worksheet.write(row, 2, account.name)
            # worksheet.write(row, 3, account.category.name)
            row += 1

    worksheet.autofit()
    workbook.close()
    output.seek(0)
    filename = "coa.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response


# def tree():
#     all = Category.objects.all()
#     sorted = []
#     levels = ['','- ','- - ','- - - ','- - - - ']
#     for node0 in all:
#         if node0.level == 0:
#             current0 = node0
#             sorted.append({'id':node0.id,'name':levels[node0.level]+node0.name})
#             for node1 in all:
#                 if node1.level == 1 and node1.parent_category == current0:
#                     current1 = node1
#                     sorted.append({'id':node1.id,'name':levels[node1.level]+node1.name})
#                     for node2 in all:
#                         if node2.level == 2 and node2.parent_category == current1:
#                             current2 = node2
#                             sorted.append({'id':node2.id,'name':levels[node2.level]+node2.name})
#                             for node3 in all:
#                                 if node3.level == 3 and node3.parent_category == current2:
#                                     current3 = node3
#                                     sorted.append({'id':node3.id,'name':levels[node3.level]+node3.name})
#                                     for node4 in all:
#                                         if node4.level == 4 and node4.parent_category == current3:
#                                             current4 = node4
#                                             sorted.append({'id':node4.id,'name':levels[node4.level]+node4.name})
#     return sorted

def tree():
    categories = Category.objects.all()
    sorted_categories = []

    def build_tree(category, level):
        sorted_categories.append({'id': category.id, 'name': '- ' * level + ' ' + category.name})
        children = categories.filter(parent_category=category)
        for child in children:
            build_tree(child, level + 1)

    root_categories = categories.filter(level=0)
    for root_category in root_categories:
        build_tree(root_category, 0)

    return sorted_categories

def generate_account_number(category):
    chunks = []
    # category = Category.objects.filter(name__iexact='debtors').first()
    parent_cat = category.parent_category
    current_cat = category
    for i in range(category.level):
        chunks.append(current_cat.category_number.zfill(2))
        current_cat = parent_cat
        parent_cat = current_cat.parent_category
    chunks.append(current_cat.category_number)
    chunks.reverse()
    counter = '1' if category.account_set.count() == 0 else str(int(category.account_set.order_by('account_number').last().account_number[-3:])+1)
    chunks.append(counter.zfill(3))
    # chunks.append(str(int(category.account_set.order_by('account_number').last().account_number[-3:])+1))
    # ic(category.account_set.all())
    str1 = ""
    for ele in chunks:
        str1 += ele

    # ic(chunks)
    # ic(str1)
    return str1

def generate_trans_number(d):
    chunks = []
    document = get_object_or_404(Document, pk=1)
    # d = date.today()
    prefix = document.prefix
    dt = datetime.strptime(d,'%Y-%m-%d')
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    # counter = '1' if Invoice.objects.count() == 0 else str(int(Invoice.objects.last().invoice_number[-3:])+1)
    counter = '1' if Transaction.objects.filter(document=document).count() == 0 else str(int(Transaction.objects.filter(document=document).last().ref.split('/')[-1])+1)
    chunks.append(prefix+'/')
    chunks.append(year+'/')
    chunks.append(month+'/')
    # chunks.append(counter.zfill(3))
    chunks.append(counter)
    str1 = ""
    for ele in chunks:
        str1 += ele

    return str1
