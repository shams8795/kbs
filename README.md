# Course Advising System

### Rule-Based Academic Course Recommendation System

Course Advising System is an academic advising application developed using Python, Streamlit, Pandas, and the Experta rule engine.

The system helps students select suitable university courses based on their academic status, completed courses, failed courses, semester plan, course prerequisites, semester availability, and allowed credit-hour load.

It also includes role-based access for students and administrators.

---

## Overview

Selecting courses can become difficult when students need to consider prerequisites, failed courses, GPA restrictions, semester offerings, and maximum credit-hour limits.

This project provides a rule-based academic advising system that evaluates these factors automatically and generates course recommendations according to predefined academic rules.

The recommendation process is handled using a Knowledge-Based System implemented with Experta.

---

## Main Features

### Student Course Recommendations

Students can provide information including:

- Current semester plan
- Current semester: Fall or Spring
- CGPA
- Passed courses
- Failed courses

The system then evaluates the student's academic information and generates suitable course recommendations.

---

### Rule-Based Academic Advising

The system uses an Experta Knowledge Engine to apply academic rules.

The implemented CGPA rules include:

- CGPA below 2.0 → Maximum 12 credit hours
- CGPA from 2.0 to below 3.0 → Maximum 18 credit hours
- CGPA of 3.0 or higher → Maximum 22 credit hours

For first-semester students, CGPA and previous course history are not required.

---

### Prerequisite Validation

Before recommending a course, the system checks whether the required prerequisite courses have already been completed.

Courses with missing prerequisites can be excluded from the recommendation list.

The system also provides the reason for excluding a course.

---

### Failed Course Priority

Failed courses receive priority during the recommendation process.

If the required prerequisites are satisfied and the course fits within the student's allowed credit-hour limit, it can be recommended for retaking.

---

### Semester-Based Recommendations

The system considers:

- Student semester plan
- Current Fall or Spring semester
- Course semester availability
- Previously completed courses
- Credit-hour restrictions

This helps prevent the recommendation of courses that are not currently available or have already been passed.

---

### Core and Elective Courses

The project supports different course groups, including:

- Core courses
- University requirements
- University electives
- Program elective courses

Elective course options can be presented according to the student's semester plan.

---

## Recommendation Output

The system can display:

- Recommended course code
- Credit hours
- Reason for recommendation
- Total recommended credit hours
- Maximum allowed credit hours
- Excluded courses
- Reason for course exclusion

A recommendation may include reasons such as:

```text
Planned course recommendation
Priority retake of failed course
Retake failed course
Core course for selected semester
University requirement
```

---

## User Roles

The application includes two user roles:

### Student

Students can use the academic advising interface to enter their academic information and generate course recommendations.

### Admin

The administrator interface provides course-data management functionality for working with the course knowledge base.

The project includes functionality for managing course information stored in CSV files.

---

## Course Data

The system uses CSV files as its local course knowledge base.

The application expects course data files such as:

```text
core_courses.csv

elective_course_1.csv
elective_course_2.csv
elective_course_3.csv
elective_course_4.csv
elective_course_5.csv
elective_course_6.csv

university_requirements.csv
university_electives.csv
```

Course information can include fields such as:

- Course code
- Course name
- Semester
- Credit hours
- Prerequisites
- Co-requisites
- Semester offered

The application also includes data-cleaning logic to normalize column names and handle different CSV encodings.

---

## How the Recommendation System Works

```text
Student Academic Information
        ↓
CGPA Evaluation
        ↓
Credit-Hour Limit
        ↓
Passed / Failed Course Analysis
        ↓
Prerequisite Validation
        ↓
Semester Availability Check
        ↓
Course Selection Rules
        ↓
Final Course Recommendations
```

---

## Knowledge-Based System

The recommendation engine is implemented using Experta.

Student information is represented as facts and academic conditions are represented as rules.

For example:

```text
IF CGPA < 2.0
THEN Maximum Credit Hours = 12
```

The rule engine evaluates the student information and determines which academic rules should be applied before generating recommendations.

---

## Technologies Used

### Python

Used for the main application logic and recommendation engine.

### Streamlit

Used to build the interactive web interface.

### Experta

Used to implement the rule-based Knowledge-Based System.

### Pandas

Used for reading, cleaning, filtering, and updating course data.

### CSV

Used as the local course knowledge base.

---

## Project Structure

```text
Course-Advising-System/
│
├── kbs_recommendation.py
├── knowledge_base_editor.py
├── README.md
└── Course CSV Files
```

`kbs_recommendation.py` contains the course recommendation logic and Streamlit interface.

`knowledge_base_editor.py` contains the role-based interface and course knowledge-base management functionality.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
```

### 2. Open the Project Directory

```bash
cd YOUR_REPOSITORY
```

### 3. Install the Required Libraries

```bash
pip install streamlit pandas experta
```

### 4. Add the Course Data

Place the required CSV course files in the project directory.

### 5. Run the Recommendation System

```bash
streamlit run kbs_recommendation.py
```

To run the interface containing the user roles and knowledge-base management:

```bash
streamlit run knowledge_base_editor.py
```

---

## Academic Logic

The recommendation process considers multiple academic constraints instead of recommending courses randomly.

The system evaluates:

- Student CGPA
- Maximum credit-hour load
- Passed courses
- Failed courses
- Course prerequisites
- Semester plan
- Course availability
- Core and elective course requirements

This allows the application to behave as a rule-based academic advising assistant.

---

## About the Project

This project was designed and developed as a Knowledge-Based Academic Advising System.

It demonstrates how rule-based Artificial Intelligence can be applied to academic course planning by combining student information, academic constraints, course data, and predefined rules to generate suitable course recommendations.

---

<h2 align="center">Course Advising System</h2>

<p align="center">
Rule-Based Academic Course Recommendation using Python, Streamlit, Pandas and Experta
</p>
