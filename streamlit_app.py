import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from io import StringIO

from students_utils import (
    load_students,
    add_student,
    update_student,
    delete_student,
    search_students,
    analyze_students,
)


st.set_page_config(page_title="Student Record Dashboard", layout="wide")


def sidebar_nav():
    st.sidebar.title("Navigation")
    return st.sidebar.radio("Go to", ["Dashboard", "Add Student", "View & Edit", "Search", "Analyze", "Import/Export"])


def dashboard_view():
    st.title("Smart Student Record Analyzer")
    df = load_students()
    if df.empty:
        st.info("No student records found. Add students or import a students.txt file.")
        return

    col1, col2, col3 = st.columns(3)
    stats = analyze_students()
    col1.metric("Total Students", stats.get("total", 0))
    col2.metric("Average Marks", f"{stats.get('average',0):.2f}")
    col3.metric("Failing Students (<40)", stats.get("failing", 0))

    st.subheader("Top / Bottom performers")
    top = df.sort_values(by="marks", ascending=False).head(5)
    bot = df.sort_values(by="marks", ascending=True).head(5)
    c1, c2 = st.columns(2)
    c1.write("Top 5")
    c1.dataframe(top.reset_index(drop=True))
    c2.write("Bottom 5")
    c2.dataframe(bot.reset_index(drop=True))

    st.subheader("Grade Distribution")
    grade_counts = df["grade"].value_counts().reset_index()
    grade_counts.columns = ["grade", "count"]
    chart = alt.Chart(grade_counts).mark_bar().encode(x="grade", y="count", color="grade")
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Marks histogram")
    hist = alt.Chart(df).mark_bar().encode(
        alt.X("marks:Q", bin=alt.Bin(maxbins=20)),
        y="count()",
    )
    st.altair_chart(hist, use_container_width=True)


def add_student_view():
    st.title("Add New Student")
    with st.form("add_student_form"):
        sid = st.number_input("Student ID", min_value=0, step=1)
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        grade = st.selectbox("Grade", ["A", "B", "C", "D", "F"]) 
        marks = st.slider("Marks", 0, 100, 50)
        submitted = st.form_submit_button("Add Student")
        if submitted:
            student = {"id": int(sid), "name": name.title(), "age": int(age), "grade": grade.upper(), "marks": int(marks)}
            ok = add_student(student)
            if ok:
                st.success("Student added successfully.")
            else:
                st.error("Student ID already exists. Use a unique ID or update the existing record.")


def view_edit_view():
    st.title("View & Edit Students")
    df = load_students()
    if df.empty:
        st.info("No student records found.")
        return
    st.dataframe(df)

    st.markdown("---")
    st.subheader("Edit / Delete a student")
    selected_id = st.selectbox("Select Student ID to edit", options=df["id"].tolist())
    row = df[df["id"] == selected_id].iloc[0]
    with st.form("edit_student"):
        name = st.text_input("Name", value=row["name"]) 
        age = st.number_input("Age", min_value=0, max_value=120, value=int(row["age"]))
        grade = st.selectbox("Grade", ["A","B","C","D","F"], index=["A","B","C","D","F"].index(row["grade"]))
        marks = st.slider("Marks", 0, 100, int(row["marks"]))
        update = st.form_submit_button("Update")
        delete = st.form_submit_button("Delete")
        if update:
            ok = update_student(int(selected_id), {"name": name.title(), "age": int(age), "grade": grade.upper(), "marks": int(marks)})
            if ok:
                st.success("Student updated.")
            else:
                st.error("Failed to update student.")
        if delete:
            if st.confirm("Are you sure you want to delete this student?"):
                ok = delete_student(int(selected_id))
                if ok:
                    st.success("Student deleted.")
                else:
                    st.error("Failed to delete student.")


def search_view():
    st.title("Search Students")
    q = st.text_input("Enter Student ID or Name substring")
    if st.button("Search"):
        res = search_students(q)
        if res.empty:
            st.info("No matching students.")
        else:
            st.dataframe(res)


def analyze_view():
    st.title("Analyze Students")
    df = load_students()
    if df.empty:
        st.info("No student data to analyze.")
        return
    stats = analyze_students()
    st.metric("Total Students", stats.get("total", 0))
    st.metric("Average Marks", f"{stats.get('average',0):.2f}")
    st.metric("Students below average", stats.get("below_average", 0))
    st.metric("Failing (<40)", stats.get("failing", 0))

    st.subheader("Grade counts")
    st.write(stats.get("grade_counts", {}))

    st.subheader("Marks distribution")
    st.bar_chart(df["marks"]) 


def import_export_view():
    st.title("Import / Export")
    st.subheader("Export students as CSV")
    df = load_students()
    if not df.empty:
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name="students_export.csv", mime="text/csv")
    else:
        st.info("No data to export.")

    st.markdown("---")
    st.subheader("Import students from CSV")
    uploaded = st.file_uploader("Upload CSV (id,name,age,grade,marks)", type=["csv","txt"])
    if uploaded is not None:
        try:
            df_in = pd.read_csv(uploaded, header=None)
            if df_in.shape[1] < 5:
                st.error("File must have 5 columns: id,name,age,grade,marks")
            else:
                df_in = df_in.iloc[:, :5]
                df_in.columns = ["id","name","age","grade","marks"]
                # append
                cur = load_students()
                merged = pd.concat([cur, df_in], ignore_index=True)
                # attempt to coerce types
                merged["id"] = merged["id"].astype(int)
                merged["age"] = merged["age"].astype(int)
                merged["marks"] = merged["marks"].astype(int)
                merged["name"] = merged["name"].astype(str).str.title()
                merged["grade"] = merged["grade"].astype(str).str.upper()
                # remove duplicate IDs keeping last
                merged = merged.drop_duplicates(subset=["id"], keep="last")
                from students_utils import save_students
                save_students(merged)
                st.success("Imported and saved students. Refresh the View page to see updates.")
        except Exception as e:
            st.error(f"Failed to import: {e}")


def main():
    page = sidebar_nav()
    if page == "Dashboard":
        dashboard_view()
    elif page == "Add Student":
        add_student_view()
    elif page == "View & Edit":
        view_edit_view()
    elif page == "Search":
        search_view()
    elif page == "Analyze":
        analyze_view()
    elif page == "Import/Export":
        import_export_view()


if __name__ == "__main__":
    main()
