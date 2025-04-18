from tabula import read_pdf
import time
import polars as pl
import xlsxwriter

depart_names_list = []
course_code_list = []



def extract_pdf_tables(pdf_path):
    try:
        print("> Starting Table Extraction ....")
        tables_list = read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True, pandas_options={'header': None})
        return pl.concat([pl.from_pandas(table) for table in tables_list], how="diagonal")

    except Exception as e:
        print(f'Error in Table Extraction: {e}')
        return None


def split_departments(big_table):
    try:
        print("> Splitting each department ....")
        boolean_mask = big_table["0"].str.contains("Generated")
        groups = boolean_mask.cum_sum()
        big_table = big_table.with_columns(pl.Series("groups", groups))
        return [depart.drop("groups") for _, depart in big_table.group_by("groups") if depart.height > 1]

    except Exception as e:
        print(f"Error in Department Splitting: {e}")
        return []


def split_grade(table):
    global depart_names_list
    global course_code_list
    student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    try:
        print("> Splitting Grades ....")
        course_code_regex = (r"^[A-Z]{3}\d{3}$")
        #check if column0 row contain course code; if yes concat column0 with column1 with seperator "-"
        #and add to new column,else add col0 to new column named "col1"
        table = table.with_columns(
            pl.when(pl.col("0").str.contains(course_code_regex))
            .then(pl.concat_str(
                    [pl.col("0"),pl.col("1")],
                    separator=" - ",
                )
            )
            .otherwise(pl.col("0"))
            .alias("col1")
        )
        #creating list of course codes
        #extrat all regex statisfying values to a new series
        #then explode the series and delete null columns and convert it to list
        course_code_list = table.select(
            pl.col("0")
            .str.extract_all(course_code_regex)
        )["0"].explode().drop_nulls().to_list()
        #use course codes in list to create regex,this is then used to
        #extract the grades create a new column based on the course code
        for course_code in course_code_list:
            table = table.with_columns(
                pl.col("1")
                .str.extract(rf"{course_code}\(([^)]+)\)")
                .alias(course_code)
            )
        #drop the old columns with seperated course code and course name
        table = table.drop(["0","1"])

        #storing the dept names to global variable
        department_name = (
            table["col1"].str.extract(student_id_pattern, group_index=3)
            .drop_nulls()
            .unique()
            .item()
        )
        depart_names_list.append(department_name)

        table_pretty = prettier_table(table, course_code_list)
        table_analyzed = analyze_table(table_pretty)
        return table_analyzed
        # return table_pretty

    except Exception as e:
        print(f"Error in Splitting Grades: {e}")


def prettier_table(table, course_code_list):
    try:
        print("> Prettifying Grades ....")
        student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
        course_code_name_pattern = r'^([A-Z]{3}\d{3})\s*-\s*(.+)$'

        #sorting student id using batch year
        df_extracted = table.with_columns([
            pl.col("col1").str.extract(student_id_pattern, group_index=1).alias("prefix"), #later using to categorize
            pl.col("col1").str.extract(student_id_pattern, group_index=2).cast(pl.Int32).alias("batch_year"), #group_index 2 means 2nd value in regex exp
        ]).sort("batch_year")

        #filter out the neccessary rows into individual tables, for prettifying the whole data
        df_depart_name = df_extracted.filter(pl.col("col1").str.contains("Generated")).drop(["prefix","batch_year"])#CSE Engg..Heading.
        df_course_code = df_extracted.filter(pl.col("col1").str.contains("Course Code")).drop(["prefix","batch_year"])#"Course Code Heading"
        df_subjects = df_extracted.filter(pl.col("col1").str.contains(course_code_name_pattern)).drop(["prefix", "batch_year"]) #coursecode-coursename rows
        df_lat_entry = df_extracted.filter(pl.col("prefix").str.len_bytes() == 4).drop(["prefix","batch_year"]) #LAT grades("LVAS" is 4 letters)
        df_norm_entry = df_extracted.filter(pl.col("prefix").str.len_bytes() == 3).drop(["prefix","batch_year"]) #Normal grades("VAS" is 3 letters)

        #initialise a blank row for adding aesthetics in between the rows
        df_blank_row = pl.DataFrame([{col: "" for col in df_norm_entry.columns}])
        #making a list of course codes and inserting Register No in the first position of the list
        #this list is then applied before grades
        custom_course_code_list = course_code_list[:]
        custom_course_code_list.insert(0, "Register No") #adding a null to make the cols count correct
        df_reg_and_codes = pl.DataFrame([custom_course_code_list], schema=df_blank_row.columns, orient="row")#orient row gives the horizontal modification

        #concating the tables together to get prettifyed table
        concated_table = pl.concat(
            [
               df_depart_name,
               df_blank_row,
               df_blank_row,
               df_course_code,
               df_subjects,
               df_blank_row,
               df_blank_row,
               df_reg_and_codes,
               df_lat_entry,
               df_norm_entry
            ],
            how="vertical_relaxed" #relaxed allows the joining of values even if there is type mismatch upto a extent
        )
        return concated_table

    except Exception as e:
        print(f"Error in Prettifying Tables: {e}")


def analyze_table(table):
    global course_code_list
    student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    try:
        # creating Arrears column
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
                )
                .alias("Arrears")
           )

        analyzis_list = []
        df_total_students =  table.select(pl.col("col1").str.contains(student_id_pattern).sum().alias("Total_Students"))
        total_students =  df_total_students["Total_Students"][0]
        analyzis_list.append(f"Total Number of Students: {total_students}")
        return table            

    except Exception as e:
        print(f"Error in Analyzing Tables: {e}")


def output_to_excel(departs_list, output_path="output.xlsx"):
    global depart_names_list
    try:
        with xlsxwriter.Workbook(output_path) as workbook:
            for i, df in enumerate(departs_list):
                df.write_excel(workbook=workbook, worksheet=f"{depart_names_list[i]}", autofit=True, autofilter=None, include_header=True, table_style="Table Style Light 8")
        print(output_path)
        return output_path
    except Exception as e:
        print(f"Error in Exporting to Excel: {e}")
        return None


def process_pdf(pdf_path):
    start_time = time.time()

    # Extract tables from PDF
    big_table = extract_pdf_tables(pdf_path)
    if big_table is None:
        print("> Failed to extract tables")
        return None

    # Split tables into departments
    departs_list = split_departments(big_table)
    # Split grades for each department
    grades_list = [split_grade(table) for table in departs_list]
    # Export to Excel
    output_file = output_to_excel(grades_list, output_path=pdf_path.parent/"processed_output.xlsx")
    # output_file = output_to_excel(grades_list, output_path="output.xlsx")
    time_taken = round(time.time() - start_time, 2)
    print(f"--Total time taken = {time_taken}s ")
    print("> Successfully Exported 😉")

    global depart_names_list
    del depart_names_list
    return output_file

# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
