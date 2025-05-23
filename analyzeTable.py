import polars as pl
import re

def analyze_courses(table, courses):
    pass_count_list =[]
    fail_count_list =[]
    pass_percentage_list =[]

    s_count_list=[];a_plus_count_list=[];b_plus_count_list=[];c_plus_count_list=[]
    a_count_list=[];b_count_list=[];c_count_list=[];d_count_list=[];p_count_list=[];f_count_list=[]

    for course in courses:
        students_count = table.select((pl.col(course).is_not_null()).arg_true()).count().item()
        fail_count = table.select((pl.col(course).str.contains("F|Absent|TBP\\*|Withheld|FE")).arg_true()).count().item()

        s_count = table.filter(pl.col(course)=="S").height
        a_plus_count = table.filter(pl.col(course)=="A+").height
        a_count = table.filter(pl.col(course)=="A").height
        b_plus_count = table.filter(pl.col(course)=="B+").height
        b_count = table.filter(pl.col(course)=="B").height
        c_plus_count = table.filter(pl.col(course)=="C+").height
        c_count = table.filter(pl.col(course)=="C").height
        d_count = table.filter(pl.col(course)=="D").height
        p_count = table.filter(pl.col(course)=="P").height
        f_count = table.filter(pl.col(course)=="F").height

        pass_count = students_count - fail_count
        pass_percentage =  round((pass_count/students_count)*100, 2)

        pass_count_list.append(pass_count)
        fail_count_list.append(fail_count)
        pass_percentage_list.append(f"{pass_percentage}%")

        s_count_list.append(s_count); a_plus_count_list.append(a_plus_count); b_plus_count_list.append(b_plus_count)
        c_plus_count_list.append(c_plus_count)
        a_count_list.append(a_count); b_count_list.append(b_count); c_count_list.append(c_count); d_count_list.append(d_count)
        p_count_list.append(p_count); f_count_list.append(f_count)

        pass_percentage = round((pass_count/students_count)*100, 2)
    courses_analysis=pl.DataFrame(
        {
            "Course": courses,
            "Pass": pass_count_list,
            "Fail": fail_count_list,
            "Pass %": pass_percentage_list,
            "S": s_count_list,
            "A+": a_plus_count_list,
            "A": a_count_list,
            "B+": b_plus_count_list,
            "B": b_count_list,
            "C+": c_plus_count_list,
            "C": c_count_list,
            "D": d_count_list,
            "F": f_count_list,
            "P": p_count_list
        }
    )
    return courses_analysis


def analyze_table(table, type: str):
    course_code_regex = (r"^[A-Z]{3}\d{3}$")
    #getting only the courses from the table column names
    courses = [column for column in table.columns if re.fullmatch(course_code_regex, column)]
    courses_analysis=analyze_courses(table, courses)

    if type == "Regular" :
        # table have no null row, finding the total number of rows using shape[0] gives number of students
        total_students_count = table.shape[0]
        #failed students have arrears in the "Arrear" col of table --> string len in Arrears will be > 1
        #(here given > 2 just for safety)--> get the count of rows where this is true as scalar value
        total_fail_count = table.select((pl.col("Arrears").str.len_bytes() > 2).arg_true()).count().item()
        total_pass_count = total_students_count - total_fail_count
        total_pass_percentage = round((total_pass_count/total_students_count)*100, 2)
        general_info = [total_students_count,total_pass_count,total_fail_count,total_pass_percentage]

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
