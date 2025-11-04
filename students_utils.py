from pathlib import Path
import pandas as pd

STUDENTS_FILE = Path(__file__).parent / "students.txt"


def load_students():
    """Load students.txt into a pandas DataFrame. Returns empty DataFrame if file missing."""
    cols = ["id", "name", "age", "grade", "marks"]
    if not STUDENTS_FILE.exists():
        return pd.DataFrame(columns=cols)
    try:
        df = pd.read_csv(STUDENTS_FILE, header=None, names=cols)
        # Normalize types
        df = df.astype({"id": int, "age": int, "marks": int})
        df["name"] = df["name"].astype(str).str.title()
        df["grade"] = df["grade"].astype(str).str.upper()
        return df
    except Exception:
        # If file malformed, return empty
        return pd.DataFrame(columns=cols)


def save_students(df: pd.DataFrame):
    """Save DataFrame to students.txt in the original CSV format (no header)."""
    df_out = df.copy()
    # keep original formatting: id,name,age,grade,marks
    df_out.to_csv(STUDENTS_FILE, index=False, header=False)


def add_student(student: dict) -> bool:
    """Add a new student. student is dict with keys id,name,age,grade,marks.
    Returns True on success, False if id duplicate."""
    df = load_students()
    if not df.empty and int(student["id"]) in df["id"].astype(int).values:
        return False
    df_new = pd.DataFrame([student])
    df = pd.concat([df, df_new], ignore_index=True)
    save_students(df)
    return True


def update_student(student_id: int, updates: dict) -> bool:
    """Update student with id. Returns True if updated, False if not found."""
    df = load_students()
    if df.empty or student_id not in df["id"].astype(int).values:
        return False
    idx = df.index[df["id"] == student_id][0]
    for k, v in updates.items():
        if k in df.columns and v is not None:
            df.at[idx, k] = v
    save_students(df)
    return True


def delete_student(student_id: int) -> bool:
    """Delete student by id. Returns True if deleted, False if not found."""
    df = load_students()
    if df.empty or student_id not in df["id"].astype(int).values:
        return False
    df = df[df["id"] != student_id]
    save_students(df)
    return True


def search_students(query: str) -> pd.DataFrame:
    """Search by id or substring in name (case-insensitive)."""
    df = load_students()
    if df.empty:
        return df
    query = query.strip()
    if not query:
        return pd.DataFrame(columns=df.columns)
    # try numeric id
    try:
        qid = int(query)
        return df[df["id"] == qid]
    except ValueError:
        mask = df["name"].str.contains(query, case=False, na=False)
        return df[mask]


def analyze_students() -> dict:
    """Return simple analytics as a dict."""
    df = load_students()
    if df.empty:
        return {}
    total = len(df)
    avg = df["marks"].mean()
    highest = df.loc[df["marks"].idxmax()].to_dict()
    lowest = df.loc[df["marks"].idxmin()].to_dict()
    failing = len(df[df["marks"] < 40])
    below_avg = len(df[df["marks"] < avg])
    grade_counts = df["grade"].value_counts().to_dict()
    return {
        "total": int(total),
        "average": float(avg),
        "highest": highest,
        "lowest": lowest,
        "failing": int(failing),
        "below_average": int(below_avg),
        "grade_counts": grade_counts,
    }
