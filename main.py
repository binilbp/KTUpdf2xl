import camelot
import time
import pandas

def extract_pdf_tables(pdf_path):
    #start_time
    start_time = time.time()

    #extracting using the stream method of camelot
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    
    #report about the extraction
    print(f"Total Tables created: {tables.n}\n")  
    min_accuracy = min(table.parsing_report['accuracy'] for table in tables)
    print(f"Minimum accuracy: {min_accuracy}")

    #time taken
    timeTaken = round(time.time()-start_time,2)
    print(f"Total Time Taken ={timeTaken}s ")
