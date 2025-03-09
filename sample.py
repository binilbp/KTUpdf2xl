from tabula import read_pdf
import pandas as pd
import re

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

# Step 3: Output to Excel
def output_to_excel(sections, output_file="structured_output.xlsx"):
    print("> Writing structured data to Excel...")

    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for entry in sections:
                sheet_name = "Unknown"  # Default sheet name

                if entry["type"] == "department_header":
                    sheet_name = re.sub(r"\W+", "_", str(entry["data"].iloc[0, 0]))[:31]
                    entry["data"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)

                elif entry["type"] == "register_and_grades" and entry["department"] is not None:
                    department_name = re.sub(r"\W+", "_", str(entry["department"].iloc[0, 0]))[:31]
                    sheet_name = department_name

                    # Convert student data dictionary to DataFrame
                    student_data = pd.DataFrame({
                        "Student ID": entry["data"]["student_id"].tolist(),
                        "Grades": entry["data"]["grades"].tolist()
                    })

                    # Split grades into separate course codes and grades
                    grades_expanded = []
                    for index, row in student_data.iterrows():
                        student_id = row['Student ID']
                        grades_info = row['Grades'].split(', ')  # Assuming grades are separated by commas
                        for grade in grades_info:
                            try:
                                course_code, grade_value = grade.split('(')  # Split by '(' to separate course code and grade
                                grades_expanded.append({
                                    "Student ID": student_id,
                                    "Course Code": course_code.strip(),
                                    "Grade": grade_value.strip(') ')  # Remove trailing ')'
                                })
                            except ValueError:
                                print(f"Warning: Could not unpack grade '{grade}' for student '{student_id}'. Skipping this entry.")

                    # Create a DataFrame from the expanded grades
                    grades_df = pd.DataFrame(grades_expanded)

                    # Write department header and grades to Excel
                    entry["department"].to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)
                    grades_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=len(entry["department"]) + 2)

                    # Auto-adjust column widths
                    worksheet = writer.sheets[sheet_name]
                    for j, column in enumerate(grades_df.columns):
                        max_length = max(grades_df[column].astype(str).map(len).max(), len(str(column))) + 2
                        worksheet.set_column(j, j, max_length)

        print("> Excel file saved successfully with structured sections.")

    except Exception as e:
        print(f"Error in saving Excel: {e}")
def main(pdf_path):
    merged_table = extract_and_merge_tables(pdf_path, verbose=1)
    if merged_table is not None:
        sections = identify_sections(merged_table, verbose=1)
        output_to_excel(sections, output_file="structured_output3.xlsx")

if __name__ == "__main__":
    main("marks.pdf")