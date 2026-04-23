import xlsxwriter

workbook = xlsxwriter.Workbook('test_shapes.xlsx')
worksheet = workbook.add_worksheet()

options = {
    'width': 256,
    'height': 100,
    'x_offset': 10,
    'y_offset': 10,
    'fill': {'color': '#DAEEF3'},
    'line': {'color': 'black'},
}

worksheet.insert_textbox('A1', 'Table 1\nID: int\nName: str', options)
workbook.close()
print("Success insert_textbox")
