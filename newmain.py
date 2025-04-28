import logging
from tabula import read_pdf
import time
import polars as pl
import xlsxwriter
import pdfplumber


def extract_main_title(pdf_path):
    print("> Extracting Main Title ...")
    logging.getLogger("pdfminer").setLevel(logging.ERROR)                    # filter the specific warning about CropBox
    with pdfplumber.open(pdf_path) as pdf:
        lines = pdf.pages[0].extract_text().splitlines()
    for i, line in enumerate(lines):
        if "APJ ABDUL KALAM TECHNOLOGICAL UNIVERSITY" in line:
            main_title =lines[i : i + 4]                                     # grab this plus the next 3 lines
            return [main_title[0], main_title[-2], main_title[-1]]           # only return the relevant info
            # return "\n".join(lines[i : i + 4])
    return None


def extract_pdf_tables(pdf_path):
    try:
        print("> Starting Table Extraction ....")
        tables_list = read_pdf(
            pdf_path,
            pages="all",
            multiple_tables=True,
            lattice=True,                                                    #lattice is an extraction method
            pandas_options={'header': None}
        )
        return pl.concat(
            [pl.from_pandas(table) for table in tables_list],
             how="diagonal"
        )

    except Exception as e:
        print(f'Error in Table Extraction: {e}')



def split_departments(big_table):
    try:
        print("> Splitting Departments ...")
        boolean_mask = big_table["0"].str.contains("Generated")
        groups = boolean_mask.cum_sum()
        big_table = big_table.with_columns(pl.Series("groups", groups))
                                                                            #split the tables using "Generated" keyword 
        return [depart.drop("groups") for _, depart in big_table.group_by("groups") if depart.height > 1]

    except Exception as e:
        print(f"Error in Department Splitting: {e}")


def create_grades_partitions(table):
    student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    try:
        print("> Creating Grades Partition ...")
        course_code_list = table.select(
            pl.col("0")
            .str.extract_all(course_code_regex)
        )["0"].explode().drop_nulls().to_list()
        for course_code in course_code_list:
            table = table.with_columns(
                pl.col("1")
                .str.extract(rf"{course_code}\(([^)]+)\)")
                .alias(course_code)
            )

        table = table.drop(["0","1"])
        table = table.with_columns([
            pl.col("col1").str.extract(student_id_pattern, group_index=1).alias("prefix"), #later using to categorize
            pl.col("col1").str.extract(student_id_pattern, group_index=2).cast(pl.Int32).alias("batch_year"), #group_index 2 means 2nd value in regex exp
        ])

        print(table)

    except Exception as e:
        print(f"Error in Department Splitting: {e}")


def create_table_partitions(table):
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    course_code_name_regex = r'^([A-Z]{3}\d{3})\s*-\s*(.+)$'
    try:
        print("> Creating Title Partion  ...")
        if "Generated" in table[0, 0]:
            title = table[0, 0]
        else:
            title = None

        print("> Creating Course Codes Partition  ...")
        table = table.with_columns(
            pl.when(pl.col("0").str.contains(course_code_regex))
            .then(pl.concat_str([pl.col("0"),pl.col("1")],
                                separator=" - ",))                           #example: "CST304 - COMPILER DESIGN"
            .otherwise(pl.col("0"))
            .alias("col1")
        )
        course_codes = table.filter(pl.col("col1").str.contains(course_code_name_regex))
        
        return None


    except Exception as e:
        print(f"Error in Creating Table Partitions: {e}")



def process_pdf(pdf_path):
    start_time = time.time()

    main_title = extract_main_title(pdf_path) #used for creating table_detail
    raw_table = extract_pdf_tables(pdf_path)
    department_tables = split_departments(raw_table)
    department_tables = [create_table_partitions(table) for table in department_tables]

    print(f"Time Taken: {round(time.time() - start_time,2)}")


# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
