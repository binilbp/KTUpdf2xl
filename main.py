import logging
import outputExcel
import analyzeTable
from tabula import read_pdf
import time
import polars as pl
import xlsxwriter
import pdfplumber
import json
from pathlib import Path

progress_store = {}

def update_progress(task_id, status, percent):
    if task_id:
        progress_store[task_id] = {"status": status, "percent": percent}


def extract_main_title(pdf_path):
    try:
        print("> Extracting Main Title ...")
        logging.getLogger("pdfminer").setLevel(logging.ERROR)                    # filter the specific warning about CropBox
        with pdfplumber.open(pdf_path) as pdf:
            lines = pdf.pages[0].extract_text().splitlines()
        for i, line in enumerate(lines):
            if "APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY" in line:
                main_title =lines[i : i + 4]                                     # grab this plus the next 3 lines
                return ( [main_title[0], main_title[-2], main_title[-1]])        # only return the relevant info
                # return "\n".join(lines[i : i + 4])
        return None
    except Exception as e:
        print(f'Error in Main Title Extraction: {e}')


def extract_pdf_tables(pdf_path):
    try:
        print("> Starting Table Extraction ....")
        tables_list = read_pdf(
            pdf_path,
            pages="all",
            multiple_tables=True,
            lattice=True,
            pandas_options={'header': None}
        )
        return pl.concat([pl.from_pandas(table) for table in tables_list],how="diagonal")
    except Exception as e:
        print(f'Error in Table Extraction: {e}')


def split_departments(big_table):
    try:
        print("> Splitting Departments ...")
        boolean_mask = big_table["0"].str.contains("Generated")             #boolean_mask is a pl series
        groups = boolean_mask.cum_sum()
        big_table = big_table.with_columns(pl.Series("groups", groups))
        return [depart.drop("groups") for _, depart in big_table.group_by("groups") if depart.height > 1]
        #table with height 1 is college name , we return only height>1 tables
    except Exception as e:
        print(f"Error in Department Splitting: {e}")


def add_arrears_column(table, course_code_list):
    # creating Arrears column
    try:
        if "Arr Count" not in table.columns:
            table = table.with_columns(
                pl.lit(0).alias("Arr Count"),
            )
        if "Arrears" not in table.columns:
            table = table.with_columns(
                pl.lit("").alias("Arrears"),
            )
        for course in course_code_list:
            table = table.with_columns(
                #F Absent TBP* Withheld FE are all considered arrears
                pl.when(pl.col(course).str.contains("F|Absent|TBP\\*|Withheld|FE")) #re to idenitfy the strings
                .then(pl.concat_str([pl.col("Arrears"),pl.lit(course)],separator=" ").str.strip_chars())
                .otherwise(
                    pl.when(pl.col(course).str.contains("Debarred"))
                    .then(pl.concat_str([pl.col("Arrears"),pl.lit("Debarred")],separator=" "))
                    .otherwise(pl.col("Arrears"))
                ).alias("Arrears")
            )

            table = table.with_columns(
                #F Absent TBP* Withheld FE are all considered arrears
                pl.when(pl.col(course).str.contains("F|Absent|TBP\\*|Withheld|FE")) #re to idenitfy the strings
                .then(pl.col("Arr Count")+1)
                .otherwise(pl.col("Arr Count")).alias("Arr Count")
            )
        # #now this is a cool way of inserting a new column at specifed index, while also creating the new column based on an expression
        # but this doesnt work here, atleast dont forget the method
        # arrear_count_expression = (pl.col("Arrears").str.strip_chars().str.split(" ").list.len()).alias("Arrears Count")
        # arrear_count_position = table.get_column_index("Arrears")
        # table.insert_column(arrear_count_position, arrear_count_expression)
        return table
    except Exception as e:
        print(f"Error in Adding Arrears: {e}")


def create_results_partitions(table, course_code_regex):
    student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    try:
        course_code_list = table.select(pl.col("0")
                   .str.extract_all(course_code_regex))["0"].explode().drop_nulls().to_list()
        for course_code in course_code_list:
            table = table.with_columns(
                pl.col("1")
                .str.extract(rf"{course_code}\(([^)]+)\)")
                .alias(course_code)
            )
        table = table.drop(["1"])
        table = add_arrears_column(table, course_code_list)
        table = table.rename({"0": "Register No"})
        table = table.with_columns([
            pl.col("Register No").str.extract(student_id_pattern, group_index=1).alias("prefix"), #later using to categorize
            pl.col("Register No").str.extract(student_id_pattern, group_index=2).cast(pl.Int32).alias("batch_year"),
            #group_index 2 means 2nd value in regex exp
        ]).sort("batch_year")
        current_batch_year = table.select(pl.col("batch_year").max()).item()

        print("    Creating Supply Results  ...")
        #Arrears in supply_results mess up the column width for regular_result, hence removing Arrears in next line :(
        supply_results = table.filter(pl.col("batch_year").cast(pl.Int32)!=current_batch_year).drop(["prefix","batch_year","Arrears"])#,"Arrears Count"])
        supply_results = supply_results[[s.name for s in supply_results if not (s.null_count() == supply_results.height)]]      #drop null only columns
        if supply_results.is_empty():  #To handle case with no supply students(actually WooW for an engineering dept !!)
            supply_results = None
            print("      Carefull !! supply results empty!!")

        print("    Creating Regular Results  ...")
        regular_results = table.filter(pl.col("batch_year")==current_batch_year).drop(["prefix","batch_year"])
        regular_results = regular_results[[s.name for s in regular_results if not (s.null_count() == regular_results.height)]]  #drop null only columns
        if regular_results.is_empty():  #To handle case with no supply students(actually WooW for an enigineering dept !!)
            regular_results = None
            print("      Carefull !! regular results empty!!")
            #case to handle if only supply and no regular(but i mean wtf?..only supply? anyway gotta do what u have to do)
            worksheet_name=supply_results.select(pl.col("Register No").str.extract(student_id_pattern, group_index=3)).item(0,0)
            return (worksheet_name, regular_results, supply_results)

        worksheet_name=regular_results.select(pl.col("Register No").str.extract(student_id_pattern, group_index=3)).item(0,0)
        return (worksheet_name, regular_results, supply_results)
    except Exception as e:
        print(f"Error in creating Result Partitions {e}")


def create_table_partitions(table):
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    course_code_name_regex = r'^([A-Z]{3}\d{3})\s*-\s*(.+)$'
    try:
        print("\n> Creating Title ...")
        if "Generated" in table[0, 0]:
            title = table[0, 0]
            title = title.partition("[Full")[0] #remove everything from "(Gen", including it
        else:
            title = None

        print("> Creating Course Codes ...")
        temp_table = table.with_columns(
            pl.when(pl.col("0").str.contains(course_code_regex))
            .then(pl.concat_str([pl.col("0"),pl.col("1")],separator=" - ",))                           #example: "CST304 - COMPILER DESIGN"
            .otherwise(pl.col("0"))
            .alias("col1")
        ).drop(["0","1"])
        course_codes = temp_table.filter(pl.col("col1").str.contains(course_code_name_regex))
        course_codes = course_codes["col1"].to_list()

        print("> Creating Result Partitions  ...")
        worksheet_name, regular_results, supply_results = create_results_partitions(table, course_code_regex  )

        print("> Creating Analyzis Partitions  ...")
        # --- MODIFIED BLOCK STARTS HERE ---
        if regular_results is not None:
            regular_analysis = analyzeTable.analyze_table(regular_results, type="Regular")
            
            # 1. Clean and Rename CoursesAnalysis for Frontend
            cleaned_courses_analysis = []
            if "CoursesAnalysis" in regular_analysis and regular_analysis["CoursesAnalysis"] is not None:
                # Convert Polars DataFrame to list of dicts
                try:
                    courses_data = regular_analysis["CoursesAnalysis"].to_dicts()
                except AttributeError:
                    # Fallback if it's already a list (just in case)
                    courses_data = regular_analysis["CoursesAnalysis"]

                for course in courses_data:
                    cleaned_courses_analysis.append({
                        "Course": course.get("Course", "Unknown"),
                        "Pass": course.get("Pass", 0),
                        "Fail": course.get("Fail", 0),
                        # CRITICAL FIX: Rename "Pass %" to "PassPercentage"
                        "PassPercentage": course.get("Pass %", 0) 
                    })

            # 2. Add to frontend dictionary
            fontend_dictionary = {
                        "Department": worksheet_name,
                        "PassPercentage": regular_analysis["PassPercentage"],
                        "StudentsCount": regular_analysis["StudentsCount"],
                        "PassCount": regular_analysis["PassCount"],
                        "FailCount": regular_analysis["FailCount"],
                        "CoursesAnalysis": cleaned_courses_analysis # <--- Now included!
                    }
        else :
            regular_analysis = None
            fontend_dictionary = None
        # --- MODIFIED BLOCK ENDS HERE ---

        if supply_results is not None:
            supply_analysis = analyzeTable.analyze_table(supply_results, type="Supply")
        else :
            supply_analysis = None

        return(
            {
                "Department": worksheet_name,
                "Title": title,
                "MaxWidth": 14, #14 as per the number of grades to display
                "Subjects": course_codes,
                "SupplyResults": supply_results,
                "RegularResults": regular_results,
                "SupplyAnalysis": supply_analysis,
                "RegularAnalysis": regular_analysis
            },
            fontend_dictionary,
        )

    except Exception as e:
        print(f"Error : {e}")


def process_pdf(pdf_path, task_id=None):
    try:
        start_time = time.time()

        unique_id = pdf_path.stem 
        output_path = Path("uploads") / f"{unique_id}_output.xlsx" 

        # STEP 1
        update_progress(task_id, "Extracting PDF Title...", 10)
        main_title = extract_main_title(pdf_path)
        
        # STEP 2
        update_progress(task_id, "Extracting Tables (This may take a while)...", 30)
        raw_table = extract_pdf_tables(pdf_path)
        
        # STEP 3
        update_progress(task_id, "Splitting Departments...", 60)
        department_tables = split_departments(raw_table)

        department_tables_list = []
        frontend_list = []
        
        # STEP 4: Loop with granular progress
        total = len(department_tables)
        for i, table in enumerate(department_tables):
            # Progress moves from 60% to 90%
            percent = 60 + int(((i+1) / total) * 30)
            update_progress(task_id, f"Analyzing Department {i+1}/{total}...", percent)

            table_to_append, dict_to_append = create_table_partitions(table)
            department_tables_list.append(table_to_append)
            frontend_list.append(dict_to_append)

        # STEP 5
        update_progress(task_id, "Generating Excel Report...", 95)
        output_file = outputExcel.output_excel(main_title = main_title, output_list=department_tables_list, output_path=output_path)

        time_taken = round(time.time() - start_time, 2)
        print(f"--Total time taken = {time_taken}s ")

        # STEP 6
        update_progress(task_id, "Completed", 100)
        return output_file, frontend_list 

    except Exception as e:
        update_progress(task_id, f"Error: {e}", -1)
        print(f"Error in processing: {e}")
        return None, None

# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
