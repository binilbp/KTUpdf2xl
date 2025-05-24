import xlsxwriter
import polars as pl
from pathlib import Path

def output_excel(main_title, output_list, output_path="output.xlsx"):
    try:
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
            'align': 'left',
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

        general_format = workbook.add_format({
                'align': 'left',
                'valign': 'vcenter',
                'top': 1,
                'bottom': 1,
                'left': 1,
                'right':1
        })
        for department in output_list:
            #setting worksheet name
            if department["Department"] is not None:
                worksheet_name = department.get("Department")
            else:
                print("      Carefull !! Department name empty!!")
                #actually this condition will raise an error but just for a clear warning the above print is given
            worksheet = workbook.add_worksheet(worksheet_name)
            row_position = 0
            for line in main_title:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1,      #end col(index start form 0)
                    line,                           #merge cell string
                    main_title_format                    #merge cell format
                )
                row_position += 1

            row_position += 1               #here only +1 cuz there's already a +1 from above loop

            worksheet.merge_range(
                row_position,               #start row
                0,                          #start col
                row_position,               #end row
                department.get("MaxWidth") - 1,  #end col(index start form 0)
                department.get("Title"),         #table (dataframe)
                main_title_format           #table format
            )

            row_position += 3

            for line in department["Subjects"]:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1,      #end col(index start form 0)
                    line,                           #merge cell string
                    general_format                    #merge cell format
                )
                row_position += 1

            row_position +=3

            if department.get("SupplyResults") is not None:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1, #end col(index start form 0)
                    "Supply Results",               #merge cell string
                    title_format                    #merge cell format
                )
                row_position += 2               #leave 1 row blank

                department.get("SupplyResults").write_excel(
                    workbook=workbook,
                    worksheet = worksheet_name,
                    position =(row_position, 0),
                    column_formats={pl.selectors.all(): table_format},
                    autofilter = False,
                    header_format = {'bold':True, 'valign':'vcenter', 'border':1},
                    autofit = True
                )
                row_position += len(department.get("SupplyResults"))+3

            if department.get("RegularResults") is not None:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1, #end col(index start form 0)
                    "Regular Results",
                    title_format
                )
                row_position += 2

                print_repeat_row = row_position
                department.get("RegularResults").write_excel(
                    workbook=workbook,
                    worksheet = worksheet_name,
                    position =(row_position, 0),
                    column_formats={pl.selectors.all(): table_format},
                    autofilter = False,
                    header_format = {'bold':True, 'border':1, 'valign':'vcenter'},
                    # autofit = True
                )
                row_position += len(department.get("RegularResults"))+3

            if department.get("SupplyAnalysis") is not None:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1,      #end col(index start form 0)
                    "Supply Results Analysis",
                    title_format
                )

                row_position += 2
                department.get("SupplyAnalysis").write_excel(
                    workbook=workbook,
                    worksheet = worksheet_name,
                    position =(row_position, 0),
                    column_formats={pl.selectors.all(): table_format},
                    autofilter = False,
                    header_format = {'bold':True, 'border':1, 'valign':'vcenter'},
                    # autofit = True
                )
                row_position += len(department.get("SupplyAnalysis"))+3

            if department.get("RegularAnalysis") is not None:
                worksheet.merge_range(
                    row_position,                   #start row
                    0,                              #start col
                    row_position,                   #end row
                    department.get("MaxWidth") - 1,      #end col(index start form 0)
                    "Regular Results Analysis",
                    title_format
                )
                row_position += 2

                general_info = [
                    f"Total Students: {department["RegularAnalysis"]["StudentsCount"]}",
                    f"Passed Students: {department["RegularAnalysis"]["PassCount"]}",
                    f"Failed Students: {department["RegularAnalysis"]["FailCount"]}",
                    f"Pass Percentage: {department["RegularAnalysis"]["PassPercentage"]}%",
                ]

                for line in general_info:
                    worksheet.merge_range(
                        row_position,                   #start row
                        0,                              #start col
                        row_position,                   #end row
                        department.get("MaxWidth") - 1,      #end col(index start form 0)
                        line,               #merge cell string
                        general_format                    #merge cell format
                    )
                    row_position += 1

                department["RegularAnalysis"]["CoursesAnalysis"].write_excel(
                    workbook=workbook,
                    worksheet = worksheet_name,
                    position =(row_position, 0),
                    column_formats={pl.selectors.all(): table_format},
                    autofilter = False,
                    header_format = {'bold':True, 'border':1, 'valign':'vcenter'},
                    # autofit = True
                )
                row_position += len(department.get("RegularAnalysis"))+3


            worksheet.set_column(0, 0, 15)
            worksheet.set_column(1, department["MaxWidth"], 8)
            worksheet.repeat_rows(print_repeat_row) #repeats the row in each new page (for printing)
            worksheet.fit_to_pages(1, 0)            #one page wide scaling (fit all col in page width for printing)
            worksheet.set_landscape()
        workbook.close()

        print("> Successfully Exported 😉")
        return Path(output_path) #Return as the FilePath object to reduce type issues
    except Exception as e:
        print(f"\nError in Exporting the Excel {e}")
