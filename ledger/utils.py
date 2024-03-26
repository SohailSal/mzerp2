import xlsxwriter
import io
from django.http import HttpResponse
from .models import Category

def generate_report(ledger_data):
    # Create a new workbook and add a worksheet
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('rep')
    header1 = "&CHere is some centered text."
    footer1 = "&LHere is some left aligned text."

    worksheet.set_header(header1)
    worksheet.set_footer(footer1)
    # Define the column headers
    headers = ['Date', 'Ref', 'Description', 'Debit', 'Credit', 'Running Balance']

    # Write the column headers to the worksheet
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Sample data for the ledger
    # ledger_data = [
    #     ['2024-01-01', 'JV/001', 'Sales', 1000, 0],
    #     ['2024-01-05', 'JV/002', 'Purchase', 0, 500],
    #     ['2024-01-10', 'JV/003', 'Salary', 0, 200],
    #     ['2024-01-15', 'JV/004', 'Rent', 500, 0],
    # ]

    # Starting balance
    balance = 0

    # Write the ledger data to the worksheet
    # for row, data in enumerate(ledger_data, start=1):
    #     date, ref, description, debit, credit = data
    #     balance += float(debit) - float(credit)

    #     worksheet.write(row, 0, date)
    #     worksheet.write(row, 1, ref)
    #     worksheet.write(row, 2, description)
    #     worksheet.write(row, 3, debit)
    #     worksheet.write(row, 4, credit)
    #     worksheet.write(row, 5, balance)

    # # Write the summary
    # total_debit = sum(data[3] for data in ledger_data)
    # total_credit = sum(data[4] for data in ledger_data)
    format1 = workbook.add_format({'num_format': 'd mmmm yyyy'})
    # format1.set_num_format('d mmmm yyyy')
    format2 = workbook.add_format({'num_format': '#,##0.00'})
    worksheet.set_column(0, 0, 18)

    for row, data in enumerate(ledger_data, start=1):
        balance += float(data['debit']) - float(data['credit'])

        worksheet.write(row, 0, data['date'], format1)
        worksheet.write(row, 1, data['ref'])
        worksheet.write(row, 2, data['description'])
        worksheet.write(row, 3, data['debit'], format2)
        worksheet.write(row, 4, data['credit'], format2)
        worksheet.write(row, 5, balance, format2)

    # Write the summary
    total_debit = sum(float(data['debit']) for data in ledger_data)
    total_credit = sum(float(data['credit']) for data in ledger_data)



    worksheet.write(row + 2, 1, 'Totals')
    worksheet.write(row + 2, 3, total_debit, format2)

    # worksheet.write(row + 3, 1, 'Total Credit')
    worksheet.write(row + 2, 4, total_credit, format2)

    # Save the workbook
    worksheet.autofit()
    workbook.close()
    output.seek(0)
    filename = "django_simple.xlsx"
    response = HttpResponse(
        output,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=%s" % filename
    return response

def tree():
#    all = [i.select() for i in Category.objects.all()]
    all = Category.objects.all()
    sorted = []
    levels = ['','├','├-','├--','├---']
    for node0 in all:
        if node0.level == 0:
            current0 = node0
            sorted.append({'id':node0.id,'name':levels[node0.level]+node0.name})
            for node1 in all:
                if node1.level == 1 and node1.parent_category == current0:
                    current1 = node1
                    sorted.append({'id':node1.id,'name':levels[node1.level]+node1.name})
                    for node2 in all:
                        if node2.level == 2 and node2.parent_category == current1:
                            current2 = node2
                            sorted.append({'id':node2.id,'name':levels[node2.level]+node2.name})


    level0 = [i.select() for i in Category.objects.filter(level=0)]
    level1 = [i.select() for i in Category.objects.filter(level=1)]
    level2 = [i.select() for i in Category.objects.filter(level=2)]
    return sorted

# poe.com generated code

def build_tree(nodes, level=0):
    tree = []
    levels = ['','├','├-','├--','├---']
    for node in nodes:
        if node.level == level:
            current_node = {'id': node.id, 'name': levels[node.level] + node.name}
            children = build_tree(nodes, level + 1)
            if children:
                current_node['children'] = children
            tree.append(current_node)
    return tree

def tree2():
    nodes = Category.objects.all()
    tree = build_tree(nodes)
    return tree