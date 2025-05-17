import xlsxwriter
import polars as pl


df = pl.DataFrame({
    "Name": ["Alice", "Bob"],
    "Sales": [100, 150]
})
df1 = pl.DataFrame({
    "GName": ["Alice", "Bob"],
    "Sales": [100, 150],
    "Good":['yes','yes']
})

dict_test = {
    "Department": "CS",
    "Title": "Test Sheet",
    "Subjects":df,
    "Grades":df1,
    "MaxWidth":3
    }


output_list = [dict_test]

def output_excel(output_list, output_path="test.xlsx"):
    workbook = xlsxwriter.Workbook(output_path)
    workbook.set_properties({
        'title': 'Excel Report on KTU result pdf',
        'author': 'Accept All C00kies'
    })

    #formattings
    main_title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 2,
 
    })
    table_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'top': 2,
        'bottom': 2,
        'left': 1,
        'right':1
    })


    for table in output_list:
        start_row = 2
        #setting worksheet name
        worksheet_name = table.get("Department")
        worksheet = workbook.add_worksheet(worksheet_name)
        worksheet.merge_range(
            0, #start row
            0, #start col
            0, #end row
            table.get("MaxWidth") - 1, #end col(index start form 0)
            table.get("Title"),
            main_title_format
        )

        table.get("Subjects").write_excel(
            # table_style='Table Style Light 2',
            workbook=workbook, 
            worksheet = worksheet_name,
            position =(start_row,0),
            column_formats={pl.selectors.all(): table_format}

        )

        start_row += len(df)+1

        table.get("Grades").write_excel(
            # table_style='Table Style Light 2',
            workbook=workbook,
            worksheet = worksheet_name,
            position =(start_row, 0),
            column_formats={pl.selectors.all(): table_format}
        )

        worksheet.autofit()
        workbook.close()

def main():
    print("starting the program")
    output_excel(output_list, output_path="test.xlsx")

if __name__ == "__main__":
    main()
