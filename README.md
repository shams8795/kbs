# 📘 Course Advising System with Streamlit & Rule-Based AI

An intelligent academic advising system built with **Python**, **Streamlit**, and a **rule-based AI engine** using `experta`.  
It helps students select the most suitable courses based on their GPA, passed/failed subjects, and semester plan — while giving admins full control over course data. 🎓⚙️

---

## 🎯 Features

- 🔐 Login system with two roles: Student & Admin
- 📚 Smart course recommendations based on:
  - GPA
  - Courses passed and failed
  - Planned semester and semester offerings
- 🧠 AI rule engine using [experta](https://github.com/niltonvolpato/python-experta)
- 🛠️ Admin interface to add, edit, and delete courses
- 📁 Auto-loading and cleaning of course data from CSV files

---

## 🧰 Tech Stack

- Python 3.9+
- Streamlit
- Pandas
- Experta
- CSV files as local database

---

## 🚀 Getting Started

### 1. Clone the repository and place your course CSV files in the root directory:

- `core_courses.csv`
- `elective_course_1.csv` to `elective_course_6.csv`
- `university_requirements.csv`
- `university_electives.csv`

### 2. Install dependencies:

```bash
pip install streamlit pandas experta
- COMP201 (3 credits): Core course for semester 4  
- ELEC102 (3 credits): Elective course for semester 4  
- UNIV103 (2 credits): University requirement  
Total Credit Hours: 8 / 18
