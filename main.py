from tabula import read_pdf
import time
import polars as pl
import pyarrow
import xlsxwriter


start_time = time.time()
def extract_pdf_tables(pdf_path, verbose = 0):
    print("> Starting Table Extraction ....")

    try:
        #extracting using the lattice method of tabula, header=None set 0, 1 as cols headings
        # here tables_list is a pandas dataframe
        tables_list = read_pdf(
                pdf_path,
                pages = "all",
                multiple_tables = True,
                lattice = True,
                pandas_options={'header': None}
                )

        end_time = time.time()

        #give additional report about the extraction if verbose is =1
        if verbose == 1:
            time_taken = round(end_time-start_time,2)
            print(f"--Time taken for extraction ={time_taken}s ")

        #creating a new pl.df to h the concated result of the tables in tables_list
        big_table = pl.DataFrame()
        big_table = pl.concat([pl.from_pandas(table) for table in tables_list], how="diagonal")
        #return the concated single table
        return big_table

    except Exception as e:
        print(f'Error in Table Extraction and Concating: {e}')


def split_departments(big_table, verbose = 1):
    try:
        print("> Splitting each department ....")
        #create boolean mask according to the presence of "Generated" in each row
        boolean_mask = big_table["0"].str.contains("Generated")
        #calculating cummulative sum to differentiate departments(groups)
        groups = boolean_mask.cum_sum()
        #adding "groups" column to big_table
        big_table = big_table.with_columns(pl.Series("groups",groups))
        #storing each department as elements of a list,also removing groups col from each depart
        depart_split_list = [depart.drop("groups") for _, depart in big_table.group_by("groups")]
        #removing height 1 table (exam centre: Vidya)
        for i, depart in enumerate(depart_split_list):
            if depart.height == 1:
                depart_split_list.pop(i)
            #to do : use this looop to remove the "groups" coloumn

        return depart_split_list
    except Exception as e:
        print(f"Error in Department Splitting: {e}")


def split_grade(table):
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

    table = table.drop(["0","1"])
    return table


def output_to_excel(departs_list):
    #to do add names dynamically
    sheet_names = ["sheet1","sheet2","sheet3","sheet4","sheet5","sheet6"]
    print("> Exporting to Excel ....")
    try:
        with xlsxwriter.Workbook("output.xlsx") as workbook:
            for df, sheet_name in zip(departs_list, sheet_names):
                df.write_excel(workbook=workbook,
                    worksheet=sheet_name,
                    autofit=True,
                    table_style="Table_Style_Medium 5"
                )

    except Exception as e:
        print(f"Error in Exporting to Excel: {e}")


#todo clean unnecessary file
big_table = extract_pdf_tables("./marks.pdf", 1)
departs_list = split_departments(big_table)
grades_list = []
for table in departs_list:
    grades_list.append(split_grade(table))
output_to_excel(grades_list)

time_taken = round(time.time()-start_time,2)
print(f"--Total time taken ={time_taken}s ")
print(f"> Successfully Exported 😉")
