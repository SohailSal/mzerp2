import xlsxwriter
import io
from django.http import HttpResponse

def generate_report(ledger_data):
    # Create a new workbook and add a worksheet
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('rep')

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
    format1 = workbook.add_format()
    format1.set_num_format('d mmmm yyyy')
    format2 = workbook.add_format({'num_format': '#,##0.00'})

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
