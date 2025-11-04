# Student Management System — Streamlit Dashboard

A small student record manager built with Streamlit for viewing, adding, updating, searching and analyzing simple student data stored in `students.txt`.

This README explains what the project contains, how to run it on Windows, file formats, and how to use the included `students_utils.py` helper.

## What this project does

- Lets you add, edit, delete and search student records.
- Shows simple analytics (average marks, highest/lowest, failing count, grade distribution).
- Supports importing/exporting records in a CSV-like `id,name,age,grade,marks` format.

## Repository files

- `streamlit_app.py` — Streamlit application that provides UI for CRUD and analytics.
- `students_utils.py` — utility functions to load, save, search, and analyze `students.txt` (used by the app).
- `students.txt` — plain CSV-style text file storing student records (created automatically if missing).
- `requirements.txt` — Python dependencies required to run the app.

## Data format

The app expects each record as a single CSV line with five columns (no header):

```
id,name,age,grade,marks
```

- id: integer unique identifier
- name: string
- age: integer
- grade: short string (e.g., A, B, C)
- marks: integer (0-100)

Example line:

```
101,Jane Doe,16,A,92
```

## Quickstart (Windows cmd)

1. (Optional) Create and activate a virtual environment:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```cmd
pip install -r requirements.txt
```

3. Run the Streamlit app:

```cmd
streamlit run streamlit_app.py
```

Open the URL shown by Streamlit in your browser (usually http://localhost:8501).

## Using the app

- Add: enter student fields and click Add. Duplicate `id` values are rejected by the helper.
- View/Edit: view the table, select a record to edit and save changes.
- Search: search by id (exact) or name substring (case-insensitive).
- Analyze: view summary statistics and grade distribution.
- Import/Export: import a CSV with `id,name,age,grade,marks` or export the current dataset.

## `students_utils.py` (short API)

The helper exposes functions used by the app. Key functions:

- `load_students()` -> pandas.DataFrame — read `students.txt`; returns empty DataFrame when missing/malformed.
- `save_students(df)` — write DataFrame back to `students.txt` (no header).
- `add_student(dict)` -> bool — add a student (returns False when id already exists).
- `update_student(id, updates)` -> bool — update fields for an id.
- `delete_student(id)` -> bool — remove a student.
- `search_students(query)` -> DataFrame — search by id or name substring.
- `analyze_students()` -> dict — returns analytics: total, average, highest, lowest, failing, below_average, grade_counts.
