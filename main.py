import camelot
import time
import pandas as pd



def extract_pdf_tables(pdf_path, verbose = 0):
    print("starting table extraction ....\n")
    start_time = time.time()

    try:    #extracting using the stream method of camelot
        tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    except Exception as e:
        print(f'Error in Table Extraction: {e}')    

    end_time = time.time()

    #give additional report about the extraction if verbose is =1
    if verbose == 1:
        time_taken = round(end_time-start_time,2)
        print(f"Total Tables created: {tables.n}")
        print(f"Total Time Taken ={time_taken}s ")

        if tables.n > 0:   #if no table present, skip
            min_accuracy = min(table.parsing_report['accuracy'] for table in tables)
            print(f"Minimum accuracy: {min_accuracy}\n")

    #return tables as output for passing to the next function 
    return tables



def organize_tables(tables, verbose = 0):   
   """  to do  """     
        


def output_excel(tables, output_file = 'output.xlsx' ):
    # If tables are extracted, process them and save to an Excel file
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for i, table in enumerate(tables):
                # Write each table's dataframe to a separate sheet in the Excel fiGle
                sheet_name = f"Table_{i+1}"
                table.df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        print(f"Error in output :{e}")



def main(pdf_path, verbose=0):
    tables = extract_pdf_tables(pdf_path, verbose)
    organized_tables = organize_tables(tables, verbose)
    output_excel(organized_tables)    


if __name__ == "__main__":   
    main('marks.pdf', 1)
