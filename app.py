import os
import streamlit as st
import sqlite3
import google.generativeai as genai
import json

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
    st.title("Master DevOps Bootcamp Batch 01 Git Quiz")
    st.sidebar.title("Menu")
    st.sidebar.write("Developer: Syed Amjad Ali")
    st.sidebar.write("Save scores and view scores")

    # Initialize db
    init_db()

    # Student enters their name first
    student_name = st.text_input("Enter your name:")

    if not student_name:
        st.error("Please enter your name to proceed.")
        return

    st.write(f"Hello, {student_name}! Let's start the quiz.")

    if st.button("Start Quiz with Gemini Flash"):

        # Configure Gemini
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        try:
            # Generate questions
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
                "Create 20 multiple-choice questions about Git (Introduction, add, commit, stash, branch, merge, push, pull, pull requests). Provide 4 options and indicate the correct answer. Format your response in a valid JSON array where each object includes 'question', 'options' (array), and 'correct' (integer index starting from 0)."
            )

            questions = json.loads(response.text)
            st.success("Questions generated! Please answer them below:")

            score = 0

            for idx, q in enumerate(questions, 1):
                st.write(f"Question {idx}. {q['question']}")

                answer = st.radio(
                    label=f"Select your answer for Question {idx}",
                    options=q['options'], 
                    key=f"q{idx}",
                )

                if answer == q['options'][q['correct']]:
                    score += 1

            st.success(f"Your score is {score}/{len(questions)}")

            if st.button("Save Score to Database"):
                save_score(student_name, score)
                st.success("Your score has been successfully saved!")

            if st.button("View All Scores (Admin)"):
                scores = view_scores()
                st.table(scores)

        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")

if __name__ == "__main__":
    main()
