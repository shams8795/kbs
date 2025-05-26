import streamlit as st
import pandas as pd
import os
from kbs_recommendation import CourseAdviser, StudentInfo

# Set page config first
st.set_page_config(page_title="Course Advising System", layout="wide")

# CSS styles
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""

# Apply CSS styles
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# =============================
# 1. Load all CSV course files from the current directory
# =============================
def load_course_data():
    directory = "./"
    all_courses = pd.DataFrame()
    
    standard_columns = [
        "semester", "course code", "course name", "description",
        "pre requsit", "co-requsit", "credit hours", "semester offered"
    ]

    for file in os.listdir(directory):
        if file.endswith(".csv"):
            file_path = os.path.join(directory, file)
            if os.path.getsize(file_path) == 0:
                continue

            try:
                # Try different encodings in order
                encodings = ['utf-8', 'ISO-8859-1', 'cp1252', 'latin1']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    continue

                if df.empty:
                    continue

                df.columns = df.columns.str.strip().str.lower()
                
                # Handle university_electives.csv specifically
                if file.lower() == "university_electives.csv":
                    if len(df.columns) == 2:
                        df.columns = ["course code", "course name"]
                        df["semester"] = ""
                        df["description"] = ""
                        df["pre requsit"] = ""
                        df["co-requsit"] = ""
                        df["credit hours"] = "2"
                        df["semester offered"] = ""
                        df["source file"] = file
                        all_courses = pd.concat([all_courses, df[standard_columns + ["source file"]]], ignore_index=True)
                        continue

                if "course name.1" in df.columns and "course name" in df.columns:
                    if df["course name"].str.match(r'[A-Z]{2,}\d{3,}').all():
                        df["course code"] = df["course name"]
                        df["course name"] = df["course name.1"]

                df = df.loc[:, ~df.columns.duplicated()]
                df.columns = [col.replace("cousre name", "course name") for col in df.columns]

                missing_cols = [col for col in standard_columns if col not in df.columns]
                for col in missing_cols:
                    df[col] = ""

                df["source file"] = file
                if file.lower() == "university_requirements.csv":
                    df["credit hours"] = "2"
                elif file.lower() == "university_electives.csv":
                    df["credit hours"] = "2"
                elif "elective" in file.lower():
                    df["credit hours"] = "3"
                
                all_courses = pd.concat([all_courses, df[standard_columns + ["source file"]]], ignore_index=True)

            except Exception:
                continue

    return all_courses

def save_courses(df, filename="updated_courses.csv"):
    # Save to the main updated file
    df.to_csv(filename, index=False)
    
    # Also save changes to the original files
    for file in df["source file"].unique():
        file_df = df[df["source file"] == file]
        if not file_df.empty:
            # Drop the source file column before saving
            file_df = file_df.drop(columns=["source file"])
            file_df.to_csv(file, index=False)

def safe_read_csv(path):
    """Read a CSV file with multiple encoding attempts."""
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

# =============================
# 3. Streamlit App
# =============================
def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None

    # Initialize global variable for course data
    global courses_df
    courses_df = load_course_data()
    
    if courses_df is None:
        st.error("❌ Failed to load course data. Please check your CSV files.")
        return
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        # Login page
        st.title("🔒 Course Advising System - Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", key='login_btn'):
            # Validate login
            if username and password:
                if username.lower() == "admin" and password == "admin":
                    st.session_state.user_type = "admin"
                    st.session_state.logged_in = True
                elif username.lower() == "student" and password == "student":
                    st.session_state.user_type = "student"
                    st.session_state.logged_in = True
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("❌ Please enter both username and password")
        return  # Stop execution if not logged in
    
    # Apply CSS styles (already applied at the top of the file)
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Show appropriate view based on user type
    if st.session_state.user_type == "admin":
        # Add some space before the main content
        st.markdown("<br>", unsafe_allow_html=True)

        # Admin view - show course editor
        st.title("🧠 Course Advising System - Editor")
        
        if courses_df is not None:
            # First show all courses grouped by their source file
            st.write("📚 All Courses by Source File:")
            for source_file in sorted(courses_df["source file"].unique()):
                file_courses = courses_df[courses_df["source file"] == source_file]
                if not file_courses.empty:
                    st.subheader(f"📄 {source_file}")
                    st.table(file_courses)

            # Then show the categorized view
            st.write("\n📊 Categorized View:")
            
            # Main/Core Courses
            main_courses = courses_df[courses_df["source file"].str.contains("core", case=False)]
            if not main_courses.empty:
                st.subheader("📘 Main/Core Courses")
                st.table(main_courses)
            else:
                st.warning("No main courses found")

            # University Requirements
            req_courses = courses_df[courses_df["source file"].str.contains("requirements", case=False)]
            if not req_courses.empty:
                st.subheader("📙 University Requirements")
                st.table(req_courses)
            else:
                st.warning("No university requirements found")

            # Elective Courses
            elective_courses = courses_df[courses_df["source file"].str.contains("elective", case=False)]
            if not elective_courses.empty:
                st.subheader("📗 Elective Courses")
                st.table(elective_courses)
            else:
                st.warning("No elective courses found")

            # Add some space after the content
            st.markdown("<br>", unsafe_allow_html=True)

            # Logout button
            if st.button("Logout", key='logout_btn_admin_bottom'):
                st.session_state.logged_in = False
                st.session_state.user_type = None
                st.experimental_rerun()

    elif st.session_state.user_type == "student":
        # Logout button
        if st.button("Logout", key='logout_btn_student_top'):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.experimental_rerun()

        # Add some space before the main content
        st.markdown("<br>", unsafe_allow_html=True)

        # Student view - course recommendation system
        st.title("🎓 Course Advising System - Student")

        # Get student input
        semester_plan = st.text_input("Enter your Semester Plan (e.g. 1 for first semester): ")
        current_semester = st.text_input("Enter your current Semester (Fall or Spring): ").strip()
        
        if semester_plan and current_semester:
            # Get CGPA and courses for non-first semester
            if semester_plan != "1":
                cgpa = st.number_input("Enter your CGPA:", min_value=0.0, max_value=4.0, value=3.0)
                passed_courses = st.text_input("Enter passed courses (by course code) separated by commas:").split(',')
                failed_courses = st.text_input("Enter failed courses (by course code) separated by commas:").split(',')
                passed_courses = [c.strip().upper() for c in passed_courses if c.strip()]
                failed_courses = [c.strip().upper() for c in failed_courses if c.strip()]
            else:
                cgpa = 3.0
                passed_courses = []
                failed_courses = []

            # Create and run the recommendation engine
            engine = CourseAdviser()
            engine.reset()
            engine.declare(StudentInfo(
                CGPA=cgpa,
                SemesterPlan=semester_plan,
                CurrentSemester=current_semester,
                Passed=passed_courses,
                Failed=failed_courses
            ))
            engine.run()

            # Get semester information
            semester_num = float(semester_plan)
            core_courses = safe_read_csv("core_courses.csv")
            semester_core = core_courses[(core_courses['semester'] == semester_num) & (core_courses['semester offered'] == current_semester)]
            
            # Check if semester has electives
            elective_file = f"elective_course_{semester_plan}.csv"
            if os.path.exists(elective_file):
                elective_courses = safe_read_csv(elective_file)
                if not elective_courses.empty:
                    elective_options = []
                    for _, row in elective_courses.iterrows():
                        code = row['course code'].strip().upper()
                        if semester_core[semester_core['course code'] == code].empty:
                            elective_options.append(code)
                    
                    if elective_options:
                        selected_elective = st.selectbox("Select an elective course:", elective_options)
                    else:
                        st.write("No elective courses available for this semester.")
                else:
                    st.write("No elective courses available for this semester.")
            else:
                st.write("No elective courses available for this semester.")

            # Check if semester has university requirements
            university_courses = safe_read_csv("university_requirements.csv")
            university_options = []
            for _, row in university_courses.iterrows():
                code = row['course code'].strip().upper()
                if semester_core[semester_core['course code'] == code].empty:
                    university_options.append(code)
            
            if university_options:
                selected_university = st.selectbox("Select a university requirement:", university_options)
            else:
                st.write("No university requirements available for this semester.")

            # Add selected courses to recommendations
            if st.button("Generate Recommendations"):
                # Add core courses first
                for _, row in semester_core.iterrows():
                    code = row['course code'].strip().upper()
                    credits = float(row['credit hours']) if pd.notna(row['credit hours']) else 0.0
                    core_course = {
                        "Course Code": code,
                        "Credit Hours": credits,
                        "Reason": f"Core course for semester {semester_num}"
                    }
                    engine.recommendations.append(core_course)
                    engine.total_credits += credits

                # Add selected elective if chosen
                if 'selected_elective' in locals() and selected_elective:
                    elective_row = elective_courses[elective_courses['course code'].str.strip().str.upper() == selected_elective].iloc[0]
                    elective_credits = float(elective_row['credit hours']) if pd.notna(elective_row['credit hours']) else 0.0
                    elective_course = {
                        "Course Code": selected_elective,
                        "Credit Hours": elective_credits,
                        "Reason": f"Elective course for semester {semester_plan}"
                    }
                    engine.recommendations.append(elective_course)
                    engine.total_credits += elective_credits

                # Add selected university requirement if chosen
                if 'selected_university' in locals() and selected_university:
                    univ_row = university_courses[university_courses['course code'].str.strip().str.upper() == selected_university].iloc[0]
                    univ_credits = float(univ_row['credit hours']) if pd.notna(univ_row['credit hours']) else 0.0
                    univ_course = {
                        "Course Code": selected_university,
                        "Credit Hours": univ_credits,
                        "Reason": "University requirement"
                    }
                    engine.recommendations.append(univ_course)
                    engine.total_credits += univ_credits

                # Show final recommendations
                st.subheader("Course Recommendations")
                if engine.recommendations:
                    for rec in engine.recommendations:
                        st.write(f"- {rec['Course Code']} ({rec['Credit Hours']} credits): {rec['Reason']}")
                    st.write(f"\nTotal Credit Hours: {engine.total_credits} / {engine.max_credits}")
                else:
                    st.write("No courses could be recommended based on the current inputs.")

                if engine.exclusions:
                    st.subheader("Excluded Courses")
                    for exc in engine.exclusions:
                        st.write(f"- {exc['Course Code']}: {exc['Reason']}")


    # Only show editor features for admin users
    if st.session_state.user_type == "admin":
        # Add some space before the main content
        st.markdown("<br>", unsafe_allow_html=True)

        # Add new course section
        st.subheader("➕ Add New Course")
        with st.form("add_form"):
            new_code = st.text_input("Course Code")
            new_name = st.text_input("Course Name")
            new_description = st.text_area("Description")
            new_pre = st.text_input("Pre-requisite (optional)")
            new_co = st.text_input("Co-requisite (optional)")
            new_credits = st.number_input("Credit Hours", min_value=1, max_value=10, step=1)
            new_semester = st.text_input("Semester Offered")
            new_sem_num = st.text_input("Semester (e.g., 1, 2)")
            course_type = st.selectbox("Course Type", [
                "Core", "University Requirement", "Elective University",
                "Elective 1", "Elective 2", "Elective 3",
                "Elective 4", "Elective 5", "Elective 6"
            ])
            add_button = st.form_submit_button("Add Course")

            if add_button:
                if new_code in courses_df["course code"].astype(str).values:
                    st.warning("⚠️ This course code already exists.")
                elif new_pre and new_pre not in courses_df["course code"].astype(str).values:
                    st.error("❌ Pre-requisite not found.")
                elif new_co and new_co not in courses_df["course code"].astype(str).values:
                    st.error("❌ Co-requisite not found.")
                else:
                    file_name_map = {
                        "Core": "core_courses.csv",
                        "University Requirement": "university_requirements.csv",
                        "Elective University": "university_electives.csv",
                        "Elective 1": "elective_course_1.csv",
                        "Elective 2": "elective_course_2.csv",
                        "Elective 3": "elective_course_3.csv",
                        "Elective 4": "elective_course_4.csv",
                        "Elective 5": "elective_course_5.csv",
                        "Elective 6": "elective_course_6.csv"
                    }
                    # Set default credit hours for new courses
                    if course_type == "University Requirement":
                        new_row["credit hours"] = "2"
                    elif course_type == "Elective University":
                        new_row["credit hours"] = "2"
                    elif course_type.startswith("Elective"):
                        new_row["credit hours"] = "3"
                    selected_file = file_name_map[course_type]
                    new_row = {
                        "semester": new_sem_num,
                        "course code": new_code,
                        "course name": new_name,
                        "description": new_description,
                        "pre requsit": new_pre,
                        "co-requsit": new_co,
                        "credit hours": new_credits,
                        "semester offered": new_semester,
                        "source file": selected_file
                    }

                    if os.path.exists(selected_file):
                        existing_df = pd.read_csv(selected_file)
                        updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
                    else:
                        updated_df = pd.DataFrame([new_row])
                    updated_df.to_csv(selected_file, index=False)
                    
                    # Update the main DataFrame
                    courses_df = pd.concat([courses_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_courses(courses_df)
                    st.success("✅ Course added successfully.")

        # Create a container for the logout button
        with st.container():
            col1, col2 = st.columns([10, 1])
            with col2:
                if st.button("Logout", key='logout_btn_admin'):
                    st.session_state.logged_in = False
                    st.rerun()

        # Add some space after the logout button
        st.markdown("<br>", unsafe_allow_html=True)

        # EDIT Course
        st.subheader("✏️ Edit Existing Course")
        if courses_df is not None and "course code" in courses_df.columns:
            course_options = courses_df["course code"].dropna().astype(str).unique()
            if len(course_options) > 0:
                selected_code = st.selectbox("Select course code to edit", course_options)
                if selected_code:
                    row = courses_df[courses_df["course code"].astype(str) == selected_code].iloc[0]
                    with st.form("edit_form"):
                        edited_name = st.text_input("Course Name", row["course name"])
                        edited_description = st.text_area("Description", row["description"])
                        edited_pre = st.text_input("Pre-requisite", row["pre requsit"])
                        edited_co = st.text_input("Co-requisite", row["co-requsit"])
                        edited_credits = st.number_input(
                            "Credit Hours", min_value=1, max_value=10,
                            value=int(row["credit hours"]) if str(row["credit hours"]).isdigit() else 3
                        )
                        edited_semester = st.text_input("Semester Offered", row["semester offered"])
                        edited_sem_num = st.text_input("Semester", row["semester"])
                        edit_button = st.form_submit_button("Update Course")

                        if edit_button:
                            idx = courses_df[courses_df["course code"].astype(str) == selected_code].index[0]
                            # Update the original file
                            original_file = courses_df.at[idx, "source file"]
                            # Try different encodings when reading the original file
                            for encoding in ['utf-8', 'ISO-8859-1', 'cp1252', 'latin1']:
                                try:
                                    original_df = pd.read_csv(original_file, encoding=encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            if original_df is None:
                                st.error(f"❌ Could not read file {original_file}. Check the file encoding.")
                                return

                            # Standardize column names
                            original_df.columns = original_df.columns.str.lower().str.strip().str.replace(' +', ' ')
                            col_map = {}
                            for col in original_df.columns:
                                if 'code' in col:
                                    col_map[col] = 'course code'
                                elif 'name' in col:
                                    col_map[col] = 'course name'
                                elif 'hour' in col:
                                    col_map[col] = 'credit hours'
                            original_df.rename(columns=col_map, inplace=True)

                            # Update the row
                            original_df.loc[original_df['course code'].astype(str) == selected_code, [
                                'course name', 'description', 'pre requsit', 'co-requsit',
                                'credit hours', 'semester offered', 'semester'
                            ]] = [
                                edited_name, edited_description, edited_pre, edited_co,
                                edited_credits, edited_semester, edited_sem_num
                            ]

                            # Save changes
                            original_df.to_csv(original_file, index=False)
                            
                            # Update the main DataFrame
                            courses_df.at[idx, [
                                'course name', 'description', 'pre requsit', 'co-requsit',
                                'credit hours', 'semester offered', 'semester'
                            ]] = [
                                edited_name, edited_description, edited_pre, edited_co,
                                edited_credits, edited_semester, edited_sem_num
                            ]
                            save_courses(courses_df)
                            st.success("✅ Course updated successfully.")
            else:
                st.warning("⚠️ No available courses to edit.")
        else:
            st.warning("⚠️ No 'course code' column available.")

        # DELETE Course
        st.subheader("❌ Delete Course")
        if courses_df is not None and "course code" in courses_df.columns and len(courses_df) > 0:
            delete_options = courses_df["course code"].dropna().astype(str).unique()
            delete_code = st.selectbox("Select course code to delete", delete_options)
            if st.button("Delete Course", key='delete_btn'):
                # Delete from the original file
                original_file = courses_df[courses_df["course code"] == delete_code]["source file"].iloc[0]
                # Try different encodings when reading the original file
                for encoding in ['utf-8', 'ISO-8859-1', 'cp1252', 'latin1']:
                    try:
                        original_df = pd.read_csv(original_file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if original_df is None:
                    st.error(f"❌ Could not read file {original_file}. Check the file encoding.")
                    return
                
                # Find and remove the course
                matching_rows = original_df[original_df["course code"] == delete_code]
                if len(matching_rows) == 0:
                    st.error(f"❌ Could not find course {delete_code} in file {original_file}")
                    return
                original_df = original_df[original_df["course code"].astype(str) != delete_code]
                original_df.to_csv(original_file, index=False)
                
                # Delete from the main DataFrame
                courses_df = courses_df[courses_df["course code"].astype(str) != delete_code]
                save_courses(courses_df)
                st.success(f"🗑️ Course '{delete_code}' deleted successfully.")

if __name__ == "__main__":
    main()