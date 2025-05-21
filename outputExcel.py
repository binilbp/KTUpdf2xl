import xlsxwriter
import polars as pl

def output_excel(main_title, output_list, output_path="output.xlsx"):
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
        'font_size': 15,
        # 'border': 2,
    })

    title_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_size': 15,
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
        row_position = 0
        for line in main_title:
            worksheet.merge_range(
                row_position,                   #start row
                0,                              #start col
                row_position,                   #end row
                table.get("MaxWidth") - 1,      #end col(index start form 0)
                line,                           #merge cell string
                title_format                    #merge cell format
            )
            row_position += 1

        row_position += 1               #here only +1 cuz there's already a +1 from above loop

        worksheet.merge_range(
            row_position,               #start row
            0,                          #start col
            row_position,               #end row
            table.get("MaxWidth") - 1,  #end col(index start form 0)
            table.get("Title"),         #table (dataframe)
            main_title_format           #table format
        )

        row_position += 3

        if table.get("Subjects") is not None:
            table.get("Subjects").write_excel(
                workbook=workbook,                                      #specify the workbook
                worksheet = worksheet_name,                             #specify the woksheet name
                position =(row_position,0),                             #table print start position
                column_formats={pl.selectors.all(): subjects_format},   #apply subjects_format for all cols in pl dataframe
                autofilter = False,                                     #disable "dropdown-filter" options in header after print
                header_format = {"bold":True, 'align':'center', 'valign':'vcenter', "border":1}, #format for the headers only
                # autofit = True                                          #autosize the cells
            )
            row_position += len(table.get("Subjects"))+3                #next two row blank

        if table.get("SupplyResults") is not None:
            worksheet.merge_range(
                row_position,                   #start row
                0,                              #start col
                row_position,                   #end row
                table.get("MaxWidth") - 1,      #end col(index start form 0)
                "Supply Students",              #merge cell string
                title_format                    #merge cell format
            )

            row_position += 2               #leave 1 row blank

            table.get("SupplyResults").write_excel(
                workbook=workbook,
                worksheet = worksheet_name,
                position =(row_position, 0),
                column_formats={pl.selectors.all(): table_format},
                autofilter = False,
                header_format = {'valign':'vcenter', 'border':1},
                # autofit = True
            )
            row_position += len(table.get("SupplyResults"))+3

        if table.get("RegularResults") is not None:
            worksheet.merge_range(
                row_position,                   #start row
                0,                              #start col
                row_position,                   #end row
                table.get("MaxWidth") - 1,      #end col(index start form 0)
                "Regular Results",
                title_format
            )

            row_position += 2
            print_repeat_row = row_position
            table.get("RegularResults").write_excel(
                workbook=workbook,
                worksheet = worksheet_name,
                position =(row_position, 0),
                column_formats={pl.selectors.all(): table_format},
                autofilter = False,
                header_format = {'border':1, 'valign':'vcenter'},
                # autofit = True
            )

        worksheet.autofit()
        worksheet.repeat_rows(print_repeat_row) #repeats the row in each new page (for printing)
        worksheet.fit_to_pages(1, 0)            #one page wide scaling (fit all col in page width for printing)
        worksheet.set_landscape()
    workbook.close()
