from tabula import read_pdf
import time
import pandas as pd



def extract_pdf_tables(pdf_path, verbose = 0):
    print("starting table extraction ....\n")
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

    except Exception as e:
        print(f'Error in Table Extraction: {e}')    

    end_time = time.time()

    #give additional report about the extraction if verbose is =1
    if verbose == 1:
        time_taken = round(end_time-start_time,2)
        print(f"Total Time Taken ={time_taken}s ")

    #return tables as output for passing to the next organizing function 
    return tables_list



def organize_tables(tables_list, verbose = 0):   
    # concating all the tables in tables_list to a single table called big_table
    big_table = pd.DataFrame()  
    for table in tables_list:
        big_table = pd.concat([big_table, table]) 



    new_tables_list = []
    new_tables_list.append(big_table)
    return new_tables_list


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
