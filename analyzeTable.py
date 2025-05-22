import polars as pl

def analyze_courses(table, courses):
    pass_count_list =[]
    fail_count_list =[]
    pass_percentage_list =[]
    for course in courses:
        students_count = table.select((pl.col(course).is_not_null()).arg_true()).count().item()
        fail_count = table.select((pl.col(course).str.contains("F|Absent|TBP\\*|Withheld|FE")).arg_true()).count().item()
        pass_count = students_count - fail_count
        pass_percentage =  round((pass_count/students_count)*100, 2)


        pass_count_list.append(pass_count)
        fail_count_list.append(fail_count)
        pass_percentage_list.append(f"{pass_percentage}%")

        pass_percentage = round((pass_count/students_count)*100, 2)
    courses_analysis=pl.DataFrame(
        {
            "Course": courses,
            "Pass Count": pass_count_list,
            "Fail Count": fail_count_list,
            "Pass %": pass_percentage_list
        }
    )
    return courses_analysis


def analyze_table(table, type: str):
    # table have no null row, finding the total number of rows using shape[0] gives number of students
    total_students_count = table.shape[0]
    courses = table.columns[1:-1] #avoid the first("RegisterNO") & last("Arrears") column names
    courses_analysis=analyze_courses(table, courses)

    if type == "Regular" :
        #failed students have arrears in the "Arrear" col of table --> string len in Arrears will be > 1
        #(here given > 2 just for safety)--> get the count of rows where this is true as scalar value
        total_fail_count = table.select((pl.col("Arrears").str.len_bytes() > 2).arg_true()).count().item()
        total_pass_count = total_students_count - total_fail_count
        total_pass_percentage = round((total_pass_count/total_students_count)*100, 2)
        print(f"Total:{total_students_count}, Fails:{total_fail_count}, Pass:{total_pass_count}, Pass percent:{total_pass_percentage}")

        return{
            "StudentsCount": total_students_count,
            "PassCount": total_pass_count,
            "FailCount": total_fail_count,
            "PassPercentage": total_pass_percentage,
            "CoursesAnalysis": courses_analysis
        }

    #for supply only the course wise analysis table is returned
    elif type == "Supply":
        return courses_analysis
