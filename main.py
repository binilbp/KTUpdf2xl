from tabula import read_pdf
import time
import polars as pl
import xlsxwriter

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
    try:
        print("> Splitting Grades ....")
        course_code_regex = (r"^[A-Z]{3}\d{3}$")
        student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"

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

        table = table.drop(["0","1"])

        #sorting student id
         # Extract parts using str.extract_all and pl.concat
        df_extracted = table.with_columns([
            pl.col("col1").str.extract(student_id_pattern, group_index=1).alias("prefix"),
            pl.col("col1").str.extract(student_id_pattern, group_index=2).cast(pl.Int32).alias("batch_year"),
            pl.col("col1").str.extract(student_id_pattern, group_index=3).alias("department"),
            pl.col("col1").str.extract(student_id_pattern, group_index=4).cast(pl.Int32).alias("roll_number")
        ])

        # Create priority for prefix: LVAS → 0, VAS → 1
        df_sorted = df_extracted.with_columns([
            pl.when(pl.col("prefix").str.len_bytes() == 4).then(1)
            .when(pl.col("prefix").str.len_bytes() == 3).then(2)
            .otherwise(0).alias("prefix_priority")
        ]).sort(
            ["prefix_priority", "batch_year", "roll_number"],
            descending=[False, True, False]
        )

        df_sorted = df_sorted.drop(["prefix","batch_year","department","roll_number","prefix_priority"])
        return df_sorted

    except Exception as e:
        print(f"Error in Organising Grades: {e}")



def output_to_excel(departs_list, output_path="output.xlsx"):
    try:
        with xlsxwriter.Workbook(output_path) as workbook:
            for i, df in enumerate(departs_list):
                df.write_excel(workbook=workbook, worksheet=f"Sheet{i+1}", autofit=True,autofilter=None, table_style="Table Style Medium 5")
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
    
    time_taken = round(time.time() - start_time, 2)
    print(f"--Total time taken = {time_taken}s ")
    print("> Successfully Exported 😉")
    
    return output_file

# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
