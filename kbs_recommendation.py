import streamlit as st
import pandas as pd
from experta import KnowledgeEngine, Fact, Rule, MATCH, P
import os

# =============================
# Load course data from CSVs with safe encoding
# =============================
def safe_read_csv(path):
    try:
        df = pd.read_csv(path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding='ISO-8859-1')

    df.columns = df.columns.str.strip().str.lower().str.replace(' +', ' ', regex=True)

    col_map = {}
    for col in df.columns:
        if 'code' in col:
            col_map[col] = 'course code'
        elif 'name' in col:
            col_map[col] = 'course name'
        elif 'hour' in col:
            col_map[col] = 'credit hours'
    df.rename(columns=col_map, inplace=True)

    df.fillna('', inplace=True)
    df['source file'] = os.path.basename(path).lower()
    return df

# Load course files
core_courses = safe_read_csv("core_courses.csv")
electives_courses = pd.concat([
    safe_read_csv(f"elective_course_{i}.csv") for i in range(1, 7)
], ignore_index=True)
university_courses = safe_read_csv("university_requirements.csv")
university_courses['course code'] = university_courses['course code'].str.strip().str.upper()

class StudentInfo(Fact):
    pass

class CourseAdviser(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.recommendations = []
        self.exclusions = []
        self.total_credits = 0
        self.max_credits = 20  # Default maximum credits per semester

    @Rule(StudentInfo(CGPA=P(lambda x: x < 2.0)))
    def cgpa_low(self):
        self.max_credits = 12

    @Rule(StudentInfo(CGPA=P(lambda x: 2.0 <= x < 3.0)))
    def cgpa_mid(self):
        self.max_credits = 18

    @Rule(StudentInfo(CGPA=P(lambda x: x >= 3.0)))
    def cgpa_high(self):
        self.max_credits = 22

    @Rule(StudentInfo(SemesterPlan=MATCH.plan, CurrentSemester=MATCH.sem, Passed=MATCH.passed, Failed=MATCH.failed))
    def recommend_courses(self, plan, sem, passed, failed):
        for code in failed:
            course_row = core_courses[core_courses['course code'].str.strip().str.upper() == code]
            if course_row.empty:
                continue
            row = course_row.iloc[0]
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            unmet = [p for p in prereqs if p not in passed]
            if unmet:
                self.exclusions.append({"Course Code": code, "Reason": f"Unmet prerequisites (failed): {', '.join(unmet)}"})
                continue
            if code not in [r['Course Code'] for r in self.recommendations] and self.total_credits + credits <= self.max_credits:
                self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Priority retake of failed course"})
                self.total_credits += credits

        plan_df = core_courses[core_courses['semester'].astype(str) == str(plan)]
        plan_df = plan_df[plan_df['semester offered'].str.lower().isin([sem.lower(), 'both'])]
        for _, row in plan_df.iterrows():
            code = row['course code'].strip().upper()
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            if code.startswith("UC") or code in passed or code in [r['Course Code'] for r in self.recommendations]:
                continue
            unmet = [p for p in prereqs if p not in passed]
            if unmet:
                self.exclusions.append({"Course Code": code, "Reason": f"Unmet prerequisites: {', '.join(unmet)}"})
                continue
            if self.total_credits + credits <= self.max_credits:
                self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Planned course recommendation"})
                self.total_credits += credits

        future_df = core_courses[core_courses['semester'].astype(str) > str(plan)]
        for _, row in future_df.iterrows():
            code = row['course code'].strip().upper()
            credits = int(row['credit hours']) if str(row['credit hours']).isdigit() else 0
            prereq_col = [col for col in row.index if 'pre' in col and 'requ' in col.lower()]
            prereqs = str(row[prereq_col[0]] if prereq_col else '').strip().split(',')
            prereqs = [p.strip().upper() for p in prereqs if p.strip()]
            if code in failed and code not in [r['Course Code'] for r in self.recommendations]:
                unmet = [p for p in prereqs if p not in passed]
                if unmet:
                    continue
                if self.total_credits + credits <= self.max_credits:
                    self.recommendations.append({"Course Code": code, "Credit Hours": credits, "Reason": "Retake failed course (future semester)"})
                    self.total_credits += credits

# =============================
# Streamlit UI
# =============================
st.title("Course Recommendation System")

semester_plan = st.selectbox("Select your Semester Plan", [str(i) for i in range(1, 11)])
current_semester = st.selectbox("Select your Current Semester", ["Fall", "Spring"])

if semester_plan == "1":
    st.info("Since it's your first semester, CGPA and passed/failed courses are not required.")
    passed_courses = []
    failed_courses = []
    cgpa = 3.0
    max_credits_override = 20
else:
    cgpa = st.number_input("Enter your CGPA", min_value=0.0, max_value=4.0, step=0.01)
    passed_courses = st.text_input("Enter passed courses (by course code) separated by commas").split(',')
    passed_courses = [c.strip().upper() for c in passed_courses if c.strip()]
    failed_courses = st.text_input("Enter failed courses (by course code) separated by commas").split(',')
    failed_courses = [c.strip().upper() for c in failed_courses if c.strip()]
    max_credits_override = None

if st.button("Get Recommendations"):
    engine = CourseAdviser()
    engine.reset()
    engine.declare(StudentInfo(
        CGPA=cgpa,
        SemesterPlan=semester_plan,
        CurrentSemester=current_semester,
        Passed=passed_courses,
        Failed=failed_courses
    ))
    semester_num = float(semester_plan)
    # Filter for core courses for the selected semester and offered in the selected semester
    semester_core = core_courses[
        (core_courses['semester'] == semester_num) &
        (core_courses['semester offered'].str.lower().isin([current_semester.lower(), 'both']))
    ]
    st.write("DEBUG: Semester core courses found:", semester_core)  # Optional debug line

    if not semester_core.empty:
        for _, row in semester_core.iterrows():
            code = str(row['course code']).strip().upper()
            credits = float(row['credit hours']) if pd.notna(row['credit hours']) else 0.0
            # Only recommend if not already passed
            if credits > 0 and code not in passed_courses:
                core_course = {
                    "Course Code": code,
                    "Credit Hours": credits,
                    "Reason": f"Core course for semester {int(semester_num)}"
                }
                engine.recommendations.append(core_course)
                engine.total_credits += credits
    engine.run()
    if max_credits_override:
        engine.max_credits = max_credits_override

    # Elective Courses by Semester Mapping
    elective_mapping = {
        "4": [1],
        "5": [2, "UE"],
        "7": ["UE"],
        "9": [3, 4, "UE"],
        "10": [5, 6, "UE"]
    }
    if semester_plan in elective_mapping:
        for elective in elective_mapping[semester_plan]:
            if str(elective).isdigit():
                elective_num = int(elective)
                elective_file_mask = f"elective_course_{elective_num}.csv.csv"
                electives_group = electives_courses[electives_courses['source file'] == elective_file_mask]
                if not electives_group.empty:
                    st.subheader(f"Elective {elective_num} Courses")
                    st.dataframe(electives_group[['course code', 'course name']])
                    selected_elective = st.text_input(f"Enter the course code to take from Elective {elective_num}", key=f"elective_{elective_num}").strip().upper()
                    elective_row = electives_group[electives_group['course code'] == selected_elective]
                    if not elective_row.empty:
                        elective_course = elective_row.iloc[0]
                        elective_credits = 3
                        engine.recommendations = [
                            r for r in engine.recommendations
                            if not (r['Course Code'] == f"E{elective_num}" or r['Reason'] == "Planned course recommendation")
                        ]
                        if engine.total_credits + elective_credits <= engine.max_credits:
                            engine.recommendations.append({
                                "Course Code": elective_course['course code'],
                                "Credit Hours": elective_credits,
                                "Reason": f"Elective {elective_num}"
                            })
                            engine.total_credits += elective_credits
                            st.success(f"Added {elective_course['course code']} to your recommendations.")
            elif elective == "UE":
                st.subheader("University Elective Courses")
                st.dataframe(university_courses[['course code', 'course name']])
                selected_univ = st.text_input("Enter the course code to take from University Electives", key=f"ue_{semester_plan}").strip().upper()
                match = university_courses[university_courses['course code'] == selected_univ]
                if not match.empty:
                    crs = match.iloc[0]
                    credits = 2
                    if engine.total_credits + credits <= engine.max_credits:
                        engine.recommendations.append({
                            "Course Code": crs['course code'],
                            "Credit Hours": credits,
                            "Reason": "University Elective"
                        })
                        engine.total_credits += credits
                        st.success(f"Added {crs['course code']} to your recommendations.")

    # University Requirement Courses (for semester 1–3)
    if semester_plan in ["1", "2", "3", "8", "9"]:
        st.subheader("University Requirement Courses")
        st.dataframe(university_courses[['course code', 'course name']])
        selected_univ = st.text_input("Enter the course code to take from University Requirements", key=f"ur_{semester_plan}").strip().upper()
        match = university_courses[university_courses['course code'] == selected_univ]
        if not match.empty:
            crs = match.iloc[0]
            credits = 2
            engine.recommendations = [r for r in engine.recommendations if r['Reason'] != "University Requirement"]
            if engine.total_credits + credits <= engine.max_credits:
                engine.recommendations.append({
                    "Course Code": crs['course code'],
                    "Credit Hours": credits,
                    "Reason": "University Requirement"
                })
                engine.total_credits += credits
                st.success(f"Added {crs['course code']} to your recommendations.")

    # Final Output
    st.header("Final Recommended Courses")
    if engine.recommendations:
        st.table(pd.DataFrame(engine.recommendations))
    else:
        st.warning("No courses could be recommended based on the current inputs.")

    st.header("Excluded Courses")
    if engine.exclusions:
        st.table(pd.DataFrame(engine.exclusions))
    else:
        st.info("No courses were excluded.")

    st.markdown(f"**Total Credit Hours:** {engine.total_credits} / {engine.max_credits}")
