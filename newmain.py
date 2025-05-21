import logging
import outputExcel
from tabula import read_pdf
import time
import polars as pl
import xlsxwriter
import pdfplumber


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
        table = table.rename({"0": "Register No"})
        table = table.with_columns([
            pl.col("Register No").str.extract(student_id_pattern, group_index=1).alias("prefix"), #later using to categorize
            pl.col("Register No").str.extract(student_id_pattern, group_index=2).cast(pl.Int32).alias("batch_year"), #group_index 2 means 2nd value in regex exp
        ]).sort("batch_year")
        current_batch_year = table.select(pl.col("batch_year").max()).item()

        #supply_results
        supply_results = table.filter(pl.col("batch_year").cast(pl.Int32)!=current_batch_year).drop(["prefix","batch_year"])
        supply_results = supply_results[[s.name for s in supply_results if not (s.null_count() == supply_results.height)]]      #drop null only columns

        #regular_results
        regular_results = table.filter(pl.col("batch_year")==current_batch_year).drop(["prefix","batch_year"])
        regular_results = regular_results[[s.name for s in regular_results if not (s.null_count() == regular_results.height)]]  #drop null only columns

        #max_width is used to specify the column range for merge cell function in outputExcel; max(column number of (regular or supply results))
        max_width = max(regular_results.shape[1],supply_results.shape[1])
        worksheet_name=regular_results.select(pl.col("Register No").str.extract(student_id_pattern, group_index=3)).item(0,0)
        return (worksheet_name, max_width, regular_results, supply_results)
    except Exception as e:
        print(f"Error in creating Result Partitions {e}")


def create_table_partitions(table):
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    course_code_name_regex = r'^([A-Z]{3}\d{3})\s*-\s*(.+)$'
    try:
        print("> Creating Title Partion  ...")
        if "Generated" in table[0, 0]:
            title = table[0, 0]
            title = title.partition("[Full")[0] #remove everything from "(Gen", including it
        else:
            title = None

        print("> Creating Course Codes Partition  ...")
        temp_table = table.with_columns(
            pl.when(pl.col("0").str.contains(course_code_regex))
            .then(pl.concat_str([pl.col("0"),pl.col("1")],separator=" - ",))                           #example: "CST304 - COMPILER DESIGN"
            .otherwise(pl.col("0"))
            .alias("col1")
        ).drop(["0","1"])
        course_codes = temp_table.filter(pl.col("col1").str.contains(course_code_name_regex))
        course_codes = course_codes.rename({"col1": "Courses"})

        print("> Creating Result Partition  ...")
        worksheet_name, max_width, regular_results, supply_results = create_results_partitions(table, course_code_regex  )

        return(
            {
                "Department": worksheet_name,
                "Title": title,
                "MaxWidth": max_width,
                "Subjects": course_codes,
                "SupplyResults": supply_results,
                "RegularResults": regular_results,
            }
        )

    except Exception as e:
        print(f"Error in Creating Table Partitions: {e}")


def process_pdf(pdf_path):
    start_time = time.time()
    main_title = extract_main_title(pdf_path)
    raw_table = extract_pdf_tables(pdf_path)
    department_tables = split_departments(raw_table)
    department_tables = [create_table_partitions(table) for table in department_tables]
    # print(department_tables)
    outputExcel.output_excel(main_title = main_title, output_list=department_tables, output_path="output.xlsx")

# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
