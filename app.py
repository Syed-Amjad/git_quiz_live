import os
os.environ["GROQ_API_KEY"] = "<your_api_key>"
# app.py
import streamlit as st
import sqlite3
import os

# Optional if you want to connect to Groq API (currently not used for quiz)
# Uncomment if you wish to enable
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# ------------------------------------------------------------------------------
# Database setup
# ------------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("quiz_data.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_score(student_name, score):
    conn = sqlite3.connect("quiz_data.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores (student_name, score) VALUES (?, ?)", (student_name, score))
    conn.commit()
    conn.close()


def view_scores():
    conn = sqlite3.connect("quiz_data.db")
    c = conn.cursor()
    c.execute("SELECT * FROM scores")
    rows = c.fetchall()
    conn.close()
    return rows



# ------------------------------------------------------------------------------
# Streamlit App
# ------------------------------------------------------------------------------
def main():
    st.title("📝 Git Quiz")
    st.sidebar.title("Menu")
    st.sidebar.write("Developer: Your Name Here")
    st.sidebar.write("Save scores and view scores")

    # Initialize db
    init_db()

    # Student enters their name first
    student_name = st.text_input("Enter your name:")

    if not student_name:
        st.error("Please enter your name to proceed.")
        return

    st.write(f"Hello, {student_name}! Let's start the quiz.")
    score = 0

    for idx, q in enumerate(questions, 1):
        st.write(f"Question {idx}. {q['question']}")

        answer = st.radio("Select your answer", q['options'], key=idx)

        if answer == q['answer']:
            score += 1

    st.success(f"Your score is {score}/{len(questions)}")

    if st.button("Save Score to Database"):
        save_score(student_name, score)
        st.success("Your score has been successfully saved!")

    if st.button("View All Scores (Admin)"):
        scores = view_scores()
        st.table(scores)


if __name__ == "__main__":
    main()
