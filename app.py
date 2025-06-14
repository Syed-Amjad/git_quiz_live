import os
import streamlit as st
import sqlite3
import re
import json

import google.generativeai as genai

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
    score = 0

    # Generate questions with Gemini
    if st.button("Generate Quiz with Gemini Flash"):
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        try:
            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(
                "Create a multiple-choice quiz with 20 questions about Git fundamentals. Provide in format: [ {question, options, correct index} ] in pure JSON array format."
            )
            raw_response = response.text

            match = re.search(r'(\[.*\])', raw_response, re.MULTILINE | re.DOTALL)
            if match:
                raw_json = match.group(1)
                questions = json.loads(raw_json)
                st.success("Questions parsed successfully! Please answer them below:")

                # Store answers in a form
                user_answers = {}
                with st.form("quiz_form"):
                    for idx, q in enumerate(questions, 1):
                        st.write(f"Question {idx}. {q['question']}")

                        answer = st.radio(
                            label=f"Select your answer for Question {idx}",
                            options=q['options'], 
                            key=f"q{idx}",
                        )
                        user_answers[idx] = answer

                    submit = st.form_submit_button("Submit Quiz")

                if submit:
                    for idx, q in enumerate(questions, 1):
                        correct_option = q['options'][q['correct']]
                        if user_answers[idx] == correct_option:
                            score += 1

                    st.success(f"Your score is {score}/{len(questions)}")

                    if st.button("Save Score to Database"):
                        save_score(student_name, score)
                        st.success("Your score has been successfully saved!")

                    if st.button("View All Scores (Admin)"):
                        scores = view_scores()
                        st.table(scores)
            else:
                st.error("JSON array not found in Gemini response.")
        except Exception as e:
            st.error(f"Error generating questions: {e}")

if __name__ == "__main__":
    main()
