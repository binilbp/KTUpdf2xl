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
            lattice=True, #lattice is an extraction method
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
        return [depart.drop("groups") for _, depart in big_table.group_by("groups") if depart.height > 1]

    except Exception as e:
        print(f"Error in Department Splitting: {e}")

def create_table_partitions(table):
    student_id_pattern = r"([A-Z]+)(\d{2})([A-Z]+)(\d+)"
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    course_code_name_regex = r'^([A-Z]{3}\d{3})\s*-\s*(.+)$'
    try:
        print("> Creating Title Partion")
        title = table[0, 0]
        if title.contain("generated")
        print(title)
        print("> Creating Course Codes Partition  ...")
        #concating course code and course name; example: "CST304 - COMPILERDESIG"
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

        #COURSE CODE TABLE PARTITION
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
