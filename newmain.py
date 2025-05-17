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
        tables_list = read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True, pandas_options={'header': None})
        return pl.concat([pl.from_pandas(table) for table in tables_list],how="diagonal")
    except Exception as e:
        print(f'Error in Table Extraction: {e}')


def split_departments(big_table):
    try:
        print("> Splitting Departments ...")
        boolean_mask = big_table["0"].str.contains("Generated")
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
        print(course_code_list)
        supply_results = table.filter(pl.col("batch_year").cast(pl.Int32)!=current_batch_year).drop(["prefix","batch_year"])
        supply_results = supply_results[[s.name for s in supply_results if not (s.null_count() == supply_results.height)]] #drop null only columns
        normal_results = table.filter(pl.col("batch_year")==current_batch_year).drop(["prefix","batch_year"])
        normal_results = normal_results[[s.name for s in normal_results if not (s.null_count() == normal_results.height)]] #drop null only columns
        worksheet_name=normal_results.select(pl.col("Register No").str.extract(student_id_pattern, group_index=3)).item(0,0)

        return (worksheet_name, normal_results, supply_results)

    except Exception as e:
        print(f"Error in creating Result Partitions {e}")


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
        temp_table = table.with_columns(
            pl.when(pl.col("0").str.contains(course_code_regex))
            .then(pl.concat_str([pl.col("0"),pl.col("1")],separator=" - ",))                           #example: "CST304 - COMPILER DESIGN"
            .otherwise(pl.col("0"))
            .alias("col1")
        ).drop(["0","1"])
        course_codes = temp_table.filter(pl.col("col1").str.contains(course_code_name_regex))

        print("> Creating Result Partition  ...")
        worksheet_name, normal_results, supply_results = create_results_partitions(table, course_code_regex  )

        # normal_results.write_excel(
        #     workbook="normaltest.xlsx",
        #     # worksheet=f"{depart_names_list[i]}",
        #     autofit=True,
        #     autofilter=None,
        #     include_header=True,
        #     table_style="Table Style Light 8"
        # )
        # # supply_results.write_excel(
        #     workbook="supplytest.xlsx",
        #     # worksheet=f"{depart_names_list[i]}",
        #     autofit=True,
        #     autofilter=None,
        #     include_header=True,
        #     table_style="Table Style Light 8"
        # )

        return(
            {
                "worksheet_name": worksheet_name,
                "title": title,
                "course_codes": course_codes,
                "supply_results": supply_results,
                "normal_results": normal_results,
            }
        )

    except Exception as e:
        print(f"Error in Creating Table Partitions: {e}")


#TODO output setakkanam(combine the different generated tables and create mannually for more modification) and analyze table TT
def output_to_excel(departs_list, output_path="output.xlsx"):
    global depart_names_list
    try:
        with xlsxwriter.Workbook(output_path) as workbook:
            for i, df in enumerate(departs_list):
                df.write_excel(
                    workbook=workbook,
                    # worksheet=f"{depart_names_list[i]}",
                    autofit=True,
                    autofilter=None,
                    include_header=True,
                    table_style="Table Style Light 8"
                )
        print(output_path)
        return output_path

    except Exception as e:
        print(f"Error in Exporting to Excel: {e}")
        return None

def process_pdf(pdf_path):
    start_time = time.time()
    main_title = extract_main_title(pdf_path)
    raw_table = extract_pdf_tables(pdf_path)
    department_tables = split_departments(raw_table)
    department_tables = [create_table_partitions(table) for table in department_tables]
    print(department_tables)
    print(f"Time Taken: {round(time.time() - start_time,2)}")


# Run everything with one function
if __name__ == "__main__":
    process_pdf("./marks.pdf")
