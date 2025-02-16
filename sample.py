import camelot
import time
import pandas as pd

def extract_pdf_tables(pdf_path, output_file='output.xlsx'):
    # Record the start time
    start_time = time.time()

    # Extract tables using Camelot with customized parameters
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    print(tables.n)

    # If tables are extracted, process them and save to an Excel file
    if tables:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for i, table in enumerate(tables):
                # Write each table's dataframe to a separate sheet in the Excel file
                sheet_name = f"Table_{i+1}"
                table.df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Get the current worksheet
                worksheet = writer.sheets[sheet_name]

                # Adjust the column width based on the length of the content
                for j, col in enumerate(table.df.columns):
                    max_length = max(table.df[col].astype(str).apply(len).max(), len(str(col)))  # Get max length of the column

                    worksheet.set_column(j, j, max_length + 2)  # Add a little extra space

    else:
        print("No tables found in the PDF.")

    # Calculate and print the execution time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    extract_pdf_tables(pdf_path='marks.pdf')