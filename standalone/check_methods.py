import xlsxwriter
import io

out = io.BytesIO()
workbook = xlsxwriter.Workbook(out)
worksheet = workbook.add_worksheet()

options = {
    'type': 'line',
    'x_offset': 100,
    'y_offset': 100,
    'width': 200,
    'height': 200,
    'line': {'color': 'red'}
}

# Try add_shape
try:
    if hasattr(worksheet, 'add_shape'):
        print("has add_shape")
        worksheet.add_shape(options)
    else:
        print("Worksheet has NO add_shape")
    
    if hasattr(worksheet, 'insert_shape'):
        print("has insert_shape")
    else:
        print("Worksheet has NO insert_shape")

except Exception as e:
    print(f"Error during shape add: {e}")

workbook.close()
print("Success")
