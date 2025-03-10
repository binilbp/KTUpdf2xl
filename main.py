from tabula import read_pdf
from pdfminer.high_level import extract_text
import pandas as pd
import re

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


# Step 1: Extract and Merge Tables
def extract_and_merge_tables(pdf_path, verbose=0):
    print("> Extracting and merging tables from PDF...")

    try:
        tables_list = read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True, pandas_options={'header': None})

        if not tables_list:
            print("No tables extracted.")
            return None

        merged_table = pd.concat(tables_list, ignore_index=True)

        if verbose:
            print(f" - Extracted {len(tables_list)} tables and merged them into one.")

        return merged_table

    except Exception as e:
        print(f"Error in extracting and merging tables: {e}")
        return None

# Step 2: Identify Sections (department_header, register_and_grades)
# Step 2: Identify Sections (department_header, register_and_grades)
def identify_sections(merged_table, verbose=0):
    print("> Identifying sections in the merged table...")

    sections = []
    current_department = None
    current_register_and_grades = []
    capturing_department = False
    department_rows = []

    for _, row in merged_table.iterrows():
        first_cell = str(row.iloc[0]).strip()

        # Detect `department_header` dynamically using "Generated"
        if re.search(r"\bGenerated\b", first_cell, re.IGNORECASE):
            if current_register_and_grades:
                # Create a DataFrame for register_and_grades with two child sections
                df = pd.DataFrame(current_register_and_grades)
                df.columns = ["Student ID", "Grades"]
                sections.append({
                    "type": "register_and_grades", 
                    "data": {
                        "student_id": df["Student ID"],
                        "grades": df["Grades"]
                    }, 
                    "department": current_department
                })
                current_register_and_grades = []

            capturing_department = True
            department_rows = [row]

        elif capturing_department:
            # Skip the "Register No | Course Code (Grade)" row
            if "Register No" in first_cell and "Course Code" in str(row.iloc[1]):
                continue  # **🚀 Skip this line**

            # Continue capturing department rows until we hit student records
            if re.match(r"([A-Z]+)\d{2}[A-Z]+\d+", first_cell):  
                capturing_department = False  # Stop capturing
                department_df = pd.DataFrame(department_rows).reset_index(drop=True)
                department_df.columns = [f"Column {j+1}" for j in range(department_df.shape[1])]
                current_department = department_df
                sections.append({"type": "department_header", "data": department_df})
                current_register_and_grades.append(row)  # Start new student record section
            else:
                department_rows.append(row)

        # Detect `register_and_grades`
        elif re.match(r"([A-Z]+)\d{2}[A-Z]+\d+", first_cell):
            current_register_and_grades.append(row)

    # Append the last batch of register_and_grades
    if current_register_and_grades:
        df = pd.DataFrame(current_register_and_grades)
        df.columns = ["Student ID", "Grades"]
        sections.append({
            "type": "register_and_grades", 
            "data": {
                "student_id": df["Student ID"],
                "grades": df["Grades"]
            }, 
            "department": current_department
        })

    if verbose:
        print(f" - Identified {len(sections)} sections.")

    return sections

# Sorting function for student IDs
def extract_sort_keys(student_id):
    id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    match = re.match(id_pattern, str(student_id))
    if match:
        prefix = match.group(1)  
        batch = int(match.group(2))  
        numeric_part = int(match.group(4))  
        return (prefix != "LVAS", -batch, numeric_part)
    return (True, 0, 0)

# Step 3: Output to Excel
def output_to_excel(extracted_header, sections, output_file="trial2.xlsx"):
    print("> Writing structured data to Excel...")

    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:

            header_df = pd.DataFrame({"Exam Details": extracted_header})
            header_df.to_excel(writer, sheet_name="Exam_Info", index=False)

            worksheet = writer.sheets["Exam_Info"]
            worksheet.set_column(0, 0, 80)  # Set wide column for header    

            for entry in sections:
                sheet_name = "Unknown"

                if entry["type"] == "department_header":
                    sheet_name = re.sub(r"\W+", "_", str(entry["data"].iloc[0, 0]))[:31]
                    entry["data"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)

                elif entry["type"] == "register_and_grades" and entry["department"] is not None:
                    department_name = re.sub(r"\W+", "_", str(entry["department"].iloc[0, 0]))[:31]
                    sheet_name = department_name

                    student_data = pd.DataFrame({
                        "Student ID": entry["data"]["student_id"].tolist(),
                        "Grades": entry["data"]["grades"].tolist()
                    })

                    # Sort student IDs BEFORE processing grades
                    if 'Student ID' in student_data.columns:
                        student_data = student_data.sort_values(by='Student ID', key=lambda x: x.map(extract_sort_keys))

                    grades_expanded = []
                    course_codes = set()

                    for _, row in student_data.iterrows():  # Now sorted correctly
                        student_id = row['Student ID']
                        grades_info = re.split(r',\s*', row['Grades'])  

                        for grade in grades_info:
                            match = re.match(r'(\w+)\((.*?)\)', grade.strip())
                            if match:
                                course_code, grade_value = match.groups()
                            elif "Absent" in grade or "Withheld" in grade or "FE" in grade:
                                course_code, grade_value = grade.strip(), "Special Case"
                            else:
                                print(f"Warning: Could not extract grade from '{grade}' for student '{student_id}'. Skipping.")
                                continue  

                            grades_expanded.append({
                                "Student ID": student_id,
                                course_code: grade_value
                            })
                            course_codes.add(course_code)

                    grades_df = pd.DataFrame(grades_expanded)

                    if not grades_df.empty:
                        pivot_df = grades_df.pivot_table(index='Student ID', aggfunc='first').reset_index()
                        pivot_df = pivot_df.fillna('')
                        # **Sort pivot_df to maintain order**
                        pivot_df = pivot_df.sort_values(by='Student ID', key=lambda x: x.map(extract_sort_keys))
                    else:
                        pivot_df = pd.DataFrame(columns=["Student ID"] + sorted(course_codes))

                    column_headers = ["Student ID"] + list(pivot_df.columns[1:])
                    total_columns = len(column_headers)

                    # Yellow-marked row: Bold with "Grades" centered
                    yellow_row = ["Student ID"] + ["Grades"] + [""] * (total_columns - 2)

                    # Blue-marked row: Shifted left by 1 cell, listing course codes
                    blue_row = [""] + list(pivot_df.columns[1:])  

                    # Ensure alignment consistency
                    yellow_row = yellow_row[:total_columns]
                    blue_row = blue_row[:total_columns]

                    formatted_data = pd.concat([
                        pd.DataFrame([yellow_row], columns=column_headers),  # Bold row (yellow)
                        pd.DataFrame([blue_row], columns=column_headers),  # Shifted left row (blue)
                        pivot_df
                    ], ignore_index=True)

                    entry["department"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                    formatted_data.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(entry["department"]) + 2, header=False)

                    worksheet = writer.sheets[sheet_name]
                    workbook = writer.book

                    # Apply formatting
                    bold_format = workbook.add_format({'bold': True})
                    center_format = workbook.add_format({'align': 'center', 'bold': True})

                    # Apply bold to the yellow-marked row
                    for col in range(total_columns):
                        worksheet.write(len(entry["department"]) + 2, col, yellow_row[col], bold_format)

                    # Center-align "Grades" within the second column
                    worksheet.write(len(entry["department"]) + 2, 1, "Grades", center_format)

                    # Auto-adjust column widths dynamically
                    for col_num, col_name in enumerate(column_headers):
                        max_length = max(
                            formatted_data[col_name].astype(str).apply(len).max(),  # Longest value in column
                            len(col_name)  # Column name length
                        ) + 2  # Extra padding
                        worksheet.set_column(col_num, col_num, max_length)

                    print("> Excel file saved successfully with structured formatting and auto-adjusted column widths.")

    except Exception as e:
        print(f"Error in saving Excel: {e}")



def main(pdf_path):
    extracted_header = extract_pdf_header(pdf_path, verbose=1)
    merged_table = extract_and_merge_tables(pdf_path, verbose=1)
    if merged_table is not None:
        sections = identify_sections(merged_table, verbose=1)
        output_to_excel(extracted_header, sections, output_file="trial2.xlsx")

if __name__ == "__main__":
    main("marks.pdf")