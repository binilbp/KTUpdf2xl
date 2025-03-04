from tabula import read_pdf
import time
import pandas as pd

def extract_pdf_tables(pdf_path, verbose=0):
    print("Starting table extraction ....\n")
    start_time = time.time()
    try:
        tables_list = read_pdf(
            pdf_path,
            pages="all",
            multiple_tables=True,
            lattice=True,
            pandas_options={'header': None}
        )
        end_time = time.time()
        if verbose == 1:
            print(f"Total Time Taken = {round(end_time - start_time, 2)}s")
        return tables_list
    except Exception as e:
        print(f'Error in Table Extraction: {e}')
        return []

def organize_tables(tables_list):
    try:
        big_table = pd.concat(tables_list, ignore_index=True) if tables_list else pd.DataFrame()
        column_name_list = [f"col{i+1}" for i in range(big_table.shape[1])]
        big_table.columns = column_name_list
        organized_tables_list = split_departments(big_table)
        return organized_tables_list
    except Exception as e:
        print(f"Error in Table Organization: {e}")
        return []

def split_departments(big_table):
    try:
        department_tables = []
        split_indices = big_table[big_table.iloc[:, 0].astype(str).str.contains("Generated", na=False)].index.tolist()
        for i in range(len(split_indices)):
            start_idx = split_indices[i]
            end_idx = split_indices[i + 1] if i + 1 < len(split_indices) else big_table.shape[0]
            department_table = big_table.iloc[start_idx:end_idx].reset_index(drop=True)
            department_tables.append(department_table)
        return department_tables
    except Exception as e:
        print(f"Error in splitting departments: {e}")
        return []

def split_subjects_and_grades(department_table):
    try:
        split_index = department_table[department_table.iloc[:, 0].astype(str).str.contains("Register", na=False)].index.min()
        subjects_table = department_table.iloc[:split_index].reset_index(drop=True)
        grades_table = department_table.iloc[split_index:].reset_index(drop=True)
        return subjects_table, grades_table
    except Exception as e:
        print(f"Error in splitting subjects and grades: {e}")
        return department_table, pd.DataFrame()

def output_excel(organized_tables_list, output_file='output.xlsx'):
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for i, dept_table in enumerate(organized_tables_list):
                subjects_table, grades_table = split_subjects_and_grades(dept_table)
                sheet_name = f"Dept_{i+1}"
                workbook = writer.book
                worksheet = writer.sheets[sheet_name] = workbook.add_worksheet(sheet_name)
                
                # Define a format with borders
                border_format = workbook.add_format({'border': 1})
                
                # Write the Subjects Table
                worksheet.write(0, 0, "Subjects Table", border_format)
                for row_idx, row_data in enumerate(subjects_table.values.tolist(), start=1):
                    for col_idx, cell_data in enumerate(row_data):
                        if pd.isna(cell_data):
                            worksheet.write(row_idx, col_idx, "", border_format)
                        else:
                            worksheet.write(row_idx, col_idx, cell_data, border_format)
                
                # Write the Grades Table
                start_row = subjects_table.shape[0] + 3  # Leave a gap between tables
                worksheet.write(start_row - 1, 0, "Grades Table", border_format)
                for row_idx, row_data in enumerate(grades_table.values.tolist(), start=start_row):
                    for col_idx, cell_data in enumerate(row_data):
                        if pd.isna(cell_data):
                            worksheet.write(row_idx, col_idx, "", border_format)
                        else:
                            worksheet.write(row_idx, col_idx, cell_data, border_format)
        print("Tables Exported to Excel Successfully")
    except Exception as e:
        print(f"Error in output: {e}")

def main(pdf_path):
    tables_list = extract_pdf_tables(pdf_path)
    organized_tables_list = organize_tables(tables_list)
    output_excel(organized_tables_list)

if __name__ == "__main__":
    main('marks.pdf')
