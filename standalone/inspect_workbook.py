import xlsxwriter
workbook = xlsxwriter.Workbook('dummy.xlsx')
print([m for m in dir(workbook) if 'shape' in m])
workbook.close()
