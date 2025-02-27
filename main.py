from tabula import read_pdf
import time
import pandas as pd



def extract_pdf_tables(pdf_path, verbose = 0):
    print("Starting table extraction ....\n")
    start_time = time.time()

    try:#extracting using the lattice method of tabula, header=None set 0, 1 as cols headings

        # here tables_list is a pandas dataframe
        tables_list = read_pdf(
                pdf_path, 
                pages = "all",
                multiple_tables = True, 
                lattice = True,
                pandas_options={'header': None}
                )
        
        end_time = time.time()

        #give additional report about the extraction if verbose is =1
        if verbose == 1:
            time_taken = round(end_time-start_time,2)
            print(f"Total Time Taken ={time_taken}s ")

        #return tables as output for passing to the next organizing function 
        return tables_list


    except Exception as e:
        print(f'Error in Table Extraction: {e}')    
    

def organize_tables(tables_list, verbose = 0):   
    try:
    # concating all the tables in tables_list to a single table called big_table
        big_table = pd.DataFrame()  
        for table in tables_list:
            big_table = pd.concat([big_table, table], ignore_index=True) 

        #dynamically creating column name list
        column_name_list = []
        for column_number in range(big_table.columns.size):
            column_name_list.append(f"col{column_number+1}")  #col1, col2, col3....

        #renaming the columns using the created list
        big_table.columns = column_name_list


    #splitting the table into different seperate department tables
        organized_tables_list = split_departments(big_table, 0)
        return organized_tables_list
    

    except Exception as e:
        print(f"Error in Table Organization: {e}")



def split_departments(big_table, verbose):
    try:
        department_splitted_tables_list = []
        split_locations = []

        #find the row indexes where "Generated" is present to split tables
        for row in big_table.itertuples():
            if "Generated" in row.col1:
                split_locations.append(row.Index) 

        #here splitting the departments by traversing backward in big_table
        for row_index in reversed(split_locations):
            #all the rows from row_index to the end of the table is split into a department
            department_splitted_tables_list.append(big_table.iloc[row_index:])
            #the splitted department is then removed form the big_table
            big_table = big_table.iloc[:row_index] 

        #making the order of departments correct again
        department_splitted_tables_list = reversed(department_splitted_tables_list)

        return  department_splitted_tables_list


    except Exception as e:
        print(f"Error in splitting the departments: {e}")




def output_excel(organized_tables_list, output_file = 'output.xlsx' ):
    # If tables are extracted, process them and save to an Excel file
    try:
        if organized_tables_list:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                for i, table in enumerate(organized_tables_list):
                    # Write each table's dataframe to a separate sheet in the Excel file
                    sheet_name = f"Table_{i+1}"
                    table.to_excel(writer, sheet_name=sheet_name, index=False)

                    # Get the current worksheet
                    worksheet = writer.sheets[sheet_name]

                    # Adjust the column width based on the length of the content
                    for j, col in enumerate(table.columns):
                        max_length = max(table[col].astype(str).apply(len).max(), len(str(col)))  # Get max length of the column

                        worksheet.set_column(j, j, max_length + 2)
            print(f"Tables Exported to ExcelSheets Successfully")
    except Exception as e:
        print(f"Error in output :{e}")



def main(pdf_path, verbose=0):
    tables_list = extract_pdf_tables(pdf_path, verbose)
    organized_tables_list = organize_tables(tables_list, verbose)
    output_excel(organized_tables_list)    



if __name__ == "__main__":   
    main('marks.pdf', 1)
