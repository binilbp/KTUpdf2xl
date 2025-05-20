import xlsxwriter
import polars as pl

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
        # 'border': 2,

    })

    sub_title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        # 'border': 1,

    })

    table_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'top': 1,
        'bottom': 1,
        'left': 1,
        'right':1
    })

    subjects_format = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'top': 1,
        'bottom': 1,
        'left': 1,
        'right':1
    })

    for table in output_list:
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

        row_position = 2
        if table.get("Subjects") is not None:
            table.get("Subjects").write_excel(
                # table_style='Table Style Light 2',
                workbook=workbook,
                worksheet = worksheet_name,
                position =(row_position,0),
                column_formats={pl.selectors.all(): subjects_format},
                autofilter = False,
                header_format = {"bold":True, 'align':'center', 'valign':'vcenter', "border":1},
                autofit = True
            )
            row_position += len(table.get("Subjects"))+3

        if table.get("SupplyResults") is not None:
            worksheet.merge_range(
                row_position, #start row
                0, #start col
                row_position, #end row
                table.get("MaxWidth") - 1, #end col(index start form 0)
                "Supply Students",
                sub_title_format
            )

            row_position += 2
            table.get("SupplyResults").write_excel(
                # table_style='Table Style Light 2',
                workbook=workbook,
                worksheet = worksheet_name,
                position =(row_position, 0),
                column_formats={pl.selectors.all(): table_format},
                autofilter = False,
                header_format = {'valign':'vcenter', 'border':1},
                autofit = True
            )
            row_position += len(table.get("SupplyResults"))+3

        if table.get("RegularResults") is not None:
            worksheet.merge_range(
                row_position, #start row
                0, #start col
                row_position, #end row
                table.get("MaxWidth") - 1, #end col(index start form 0)
                "Regular Results",
                sub_title_format
            )

            row_position += 2
            print_repeat_row = row_position
            table.get("RegularResults").write_excel(
                # table_style='Table Style Light 2',
                workbook=workbook,
                worksheet = worksheet_name,
                position =(row_position, 0),
                column_formats={pl.selectors.all(): table_format},
                autofilter = False,
                header_format = {'border':1, 'valign':'vcenter'},
                autofit = True
            )

        worksheet.repeat_rows(print_repeat_row)  # Repeats the row for each page
        worksheet.fit_to_pages(1, 0) #one page wide scaling (for printing)
        worksheet.set_landscape()
        worksheet.autofit()
    workbook.close()
