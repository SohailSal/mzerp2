import xlsxwriter

# Create a new workbook and add a worksheet
workbook = xlsxwriter.Workbook('ledger.xlsx')
worksheet = workbook.add_worksheet()

# Define the column headers
headers = ['Date', 'Particulars', 'Debit', 'Credit', 'Running Balance']

# Write the column headers to the worksheet
for col, header in enumerate(headers):
    worksheet.write(0, col, header)

# Sample data for the ledger
ledger_data = [
    ['2024-01-01', 'Sales', 1000, 0],
    ['2024-01-05', 'Purchase', 0, 500],
    ['2024-01-10', 'Salary', 0, 200],
    ['2024-01-15', 'Rent', 500, 0],
]

# Starting balance
balance = 0

# Write the ledger data to the worksheet
for row, data in enumerate(ledger_data, start=1):
    date, particulars, debit, credit = data
    balance += debit - credit

    worksheet.write(row, 0, date)
    worksheet.write(row, 1, particulars)
    worksheet.write(row, 2, debit)
    worksheet.write(row, 3, credit)
    worksheet.write(row, 4, balance)

# Write the summary
total_debit = sum(data[2] for data in ledger_data)
total_credit = sum(data[3] for data in ledger_data)

worksheet.write(row + 2, 1, 'Total Debit')
worksheet.write(row + 2, 2, total_debit)

worksheet.write(row + 3, 1, 'Total Credit')
worksheet.write(row + 3, 3, total_credit)

# Save the workbook
workbook.close()