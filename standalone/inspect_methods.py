import xlsxwriter
workbook = xlsxwriter.Workbook('dummy.xlsx')
worksheet = workbook.add_worksheet()
print([m for m in dir(worksheet) if 'shape' in m or 'line' in m or 'insert' in m])
workbook.close()
