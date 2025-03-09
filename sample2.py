from tabula import read_pdf
import time
import pandas as pd
import re
from pdfminer.high_level import extract_text

def extract_pdf_header(pdf_path, verbose=0):
    print("> Extracting header text from PDF ...")
    try:
        first_page_text = extract_text(pdf_path, page_numbers=[0])
        
        match = re.search(r"APJ.*?\(S(\d) Result\)", first_page_text, re.DOTALL)
        if match:
            extracted_header = match.group(0).strip()
            header_lines = extracted_header.split("\n")  
            
            spaced_header_lines = []
            for line in header_lines:
                if line.strip():  
                    spaced_header_lines.append(line.strip())
                    spaced_header_lines.append("")  

            if verbose:
                print(" - Extracted Header (Formatted):\n" + "\n".join(spaced_header_lines))

            return spaced_header_lines
        else:
            print(" - Header not found using regex!")
            return ["Header Not Found"]

    except Exception as e:
        print(f"Error in Header Extraction: {e}")
        return ["Header Extraction Failed"]

def extract_pdf_tables(pdf_path, verbose=0):
    print("> Starting table extraction ....")
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
        if verbose:
            time_taken = round(end_time - start_time, 2)
            print(f" - Time Taken for extraction = {time_taken}s ")

        return tables_list

    except Exception as e:
        print(f'Error in Table Extraction: {e}')
        return []

def split_departments(big_table, verbose=0):
    print(" - Splitting tables into departments...") if verbose else None
    try:
        department_tables_list = []
        split_locations = []

        for row in big_table.itertuples():
            if "Generated" in str(row.col1):
                split_locations.append(row.Index)

        print(f" -- Splitting the tables using Row Indexes in reverse order") if verbose else None
        for row_index in reversed(split_locations):
            department_table = big_table.iloc[row_index:]
            department_tables_list.append(department_table)
            big_table = big_table.iloc[:row_index]

        department_tables_list = list(reversed(department_tables_list))

        print(f" -- Correcting the index of the department tables") if verbose else None
        for i, department_table in enumerate(department_tables_list):
            department_tables_list[i] = department_table.reset_index(drop=True)

        return department_tables_list
    except Exception as e:
        print(f"Error in splitting the departments: {e}")
        return []

def beautify_table(depart_no, department_table, verbose=0):
    print(f" -- Beautifying table {depart_no + 1}") if verbose else None
    try:
        course_re_pattern = r"\b[A-Z]{3}\d{3}\b"

        # Extract department header and course details
        department_header = None
        course_details = {}

        for row in department_table.itertuples():
            row_values = [str(x) for x in row[1:] if pd.notna(x)]
            row_text = " ".join(row_values)

            # Extract department header
            if "Generated on" in row_text:
                department_header = row_text.strip()

            # Extract course codes and names
            course_match = re.match(r"([A-Z]{3}\d{3})\s+(.*)", row_text)
            if course_match:
                course_code, course_name = course_match.groups()
                course_details[course_code] = course_name

        # If no header found, set a default
        if not department_header:
            department_header = "Department Info Not Found"

        # Extract student data
        unique_courses = set()
        student_data = []

        for row in department_table.itertuples():
            if isinstance(row.col1, str) and re.match(r"[A-Z]+\d{2}[A-Z]+\d+", row.col1):  # Student ID pattern
                student_id = row.col1
                courses = re.findall(r"(\b[A-Z]{3}\d{3}\b)\((.*?)\)", ' '.join(str(x) for x in row[2:]))
                student_entry = {"Register No": student_id}
                for course, grade in courses:
                    unique_courses.add(course)
                    student_entry[course] = grade
                student_data.append(student_entry)

        # Convert to DataFrame with dynamically assigned columns
        structured_df = pd.DataFrame(student_data)
        structured_df = structured_df.fillna("-")  # Fill missing grades with '-'

        # Sort student IDs properly
        id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
        def extract_sort_keys(student_id):
            match = re.match(id_pattern, str(student_id))
            if match:
                prefix = match.group(1)
                batch = int(match.group(2))
                numeric_part = int(match.group(4))
                return (prefix != "LVAS", -batch, numeric_part)
            return (True, 0, 0)

        structured_df = structured_df.sort_values(by=["Register No"], key=lambda x: x.map(extract_sort_keys)).reset_index(drop=True)

        # Create course details section
        course_df = pd.DataFrame([["Course Code", "Course Name"]] + [[code, name] for code, name in course_details.items()], columns=["Register No", "Course Name"])

        # Department header as a separate row
        header_df = pd.DataFrame([[department_header, ""]], columns=["Register No", "Course Name"])

        # Blank row for readability
        blank_df = pd.DataFrame([["", ""]], columns=["Register No", "Course Name"])

        # Move the first row to the 13th row
        if not structured_df.empty:
            first_row = structured_df.iloc[0:1]  # Get the first row
            structured_df = pd.concat([structured_df.iloc[1:], blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, blank_df, first_row], ignore_index=True)

        # Combine all sections in the correct order
        final_df = pd.concat([header_df, blank_df, course_df, blank_df, structured_df], ignore_index=True)

        return final_df
    except Exception as e:
        print(f"Error in beautifying: {e}")
        return department_table


def extract_department_code(department_table):
    try:
        for row in department_table.itertuples():
            if isinstance(row.col1, str):  
                match = re.search(r"^[A-Z]+\d{2}([A-Z]+)\d+$", row.col1)  
                if match:
                    return match.group(1).upper()  
        return "Unknown_Department"  
    except Exception as e:
        print(f"Error extracting department code: {e}")
        return "Unknown_Department"

def sort_student_ids(department_table):
    try:
        id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
        
        def extract_sort_keys(student_id):
            match = re.match(id_pattern, str(student_id))
            if match:
                prefix = match.group(1)  
                batch = int(match.group(2))  
                numeric_part = int(match.group(4))  
                return (prefix != "LVAS", -batch, numeric_part)
            return (True, 0, 0)

        if 'col1' in department_table.columns:
            student_rows = department_table[department_table['col1'].str.match(id_pattern, na=False)]
            other_rows = department_table[~department_table['col1'].str.match(id_pattern, na=False)]
            student_rows = student_rows.sort_values(by='col1', key=lambda x: x.map(extract_sort_keys))
            department_table = pd.concat([other_rows, student_rows]).reset_index(drop=True)

        return department_table
    except Exception as e:
        print(f"Error in sorting student IDs: {e}")
        return department_table

def organize_tables(tables_list, verbose=0):
    print(f"\n> Organizing the tables ....")
    organized_tables_dict = {}

    try:
        print(f" - Concatenating the tables") if verbose else None
        big_table = pd.DataFrame()
        for table in tables_list:
            big_table = pd.concat([big_table, table], ignore_index=True)

        column_name_list = [f"col{i+1}" for i in range(big_table.columns.size)]
        big_table.columns = column_name_list

        print(f" - Splitting the departments") if verbose else None
        department_tables_list = split_departments(big_table, verbose)

        print(f" - Beautifying the tables and sorting IDs") if verbose else None
        for depart_no, department_table in enumerate(department_tables_list):
            beautified_table = beautify_table(depart_no, department_table, verbose)
            sorted_table = sort_student_ids(beautified_table)
            department_code = extract_department_code(department_table)

            sheet_name = department_code
            count = 1
            while sheet_name in organized_tables_dict:
                sheet_name = f"{department_code}_{count}"  
                count += 1

            organized_tables_dict[sheet_name] = sorted_table

        return organized_tables_dict
    except Exception as e:
        print(f"Error in Table Organization: {e}")
        return {}

def output_excel(organized_tables_dict, extracted_header, output_file="output.xlsx"):
    print(f"\n> Exporting the tables and header ....")
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            header_df = pd.DataFrame({"Exam Details": extracted_header})
            header_df.to_excel(writer, sheet_name="Exam_Info", index=False)

            worksheet = writer.sheets["Exam_Info"]
            worksheet.set_column(0, 0, 80)  # Set wide column for header

            for sheet_name, table in organized_tables_dict.items():
                table.to_excel(writer, sheet_name=sheet_name, index=False)
                
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(table.columns):
                    max_length = max(table[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_length)

        print(f" - Tables and header exported to Excel successfully")
    except Exception as e:
        print(f"Error in output: {e}")

def main(pdf_path, verbose=0):
    extracted_header = extract_pdf_header(pdf_path, verbose)
    tables_list = extract_pdf_tables(pdf_path, verbose)
    organized_tables_dict = organize_tables(tables_list, verbose)
    output_excel(organized_tables_dict, extracted_header)

if __name__ == "__main__":
    main('marks.pdf', 1)