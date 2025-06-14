import os
import streamlit as st
import sqlite3
import google.generativeai as genai
import json
import re

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

    # Initialize session state variables
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'answers_submitted' not in st.session_state:
        st.session_state.answers_submitted = False
    if 'student_name' not in st.session_state:
        st.session_state.student_name = ""
    if 'show_save_button' not in st.session_state:
        st.session_state.show_save_button = False

    # Student enters their name first
    st.session_state.student_name = st.text_input("Enter your name:", value=st.session_state.student_name)

    if not st.session_state.student_name:
        st.error("Please enter your name to proceed.")
        return

    st.write(f"Hello, {st.session_state.student_name}! Let's start the quiz.")

    if st.button("Generate Quiz with Gemini Flash") and not st.session_state.questions:
        try:
            # Configure Gemini
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

            # Generate questions
            response = genai.GenerativeModel("gemini-2.0-flash").generate_content(
                """Create 20 multiple-choice questions about Git fundamentals. 
                Provide them in a pure JSON array format with each object having:
                - question
                - options (array of 4)
                - correct (integer, 0-based index of correct answer).
                """
            )

            raw_json = response.text.strip()

            # Extract array from raw_json
            match = re.search(r'(\[.*\])', raw_json, re.MULTILINE | re.DOTALL)
            if match:
                raw_json = match.group(1)
                st.session_state.questions = json.loads(raw_json)
                st.session_state.score = 0
                st.session_state.answers_submitted = False
                st.session_state.show_save_button = False
                st.success("Questions generated! Please answer them below:")
            else:
                st.error("Unable to extract questions from Gemini response.")

        except Exception as e:
            st.error(f"Error generating questions: {e}")

    if st.session_state.questions and not st.session_state.answers_submitted:
        user_answers = []
        
        for idx, q in enumerate(st.session_state.questions, 1):
            st.write(f"Question {idx}. {q['question']}")
            user_answer = st.radio(
                "Select your answer", 
                q['options'], 
                key=f"q_{idx}",
                index=None
            )
            user_answers.append(user_answer)

        if st.button("Submit Answers"):
            st.session_state.score = 0
            for idx, (q, user_answer) in enumerate(zip(st.session_state.questions, user_answers), 1):
                if user_answer == q['options'][q['correct']]:
                    st.session_state.score += 1
            
            st.session_state.answers_submitted = True
            st.session_state.show_save_button = True
            st.success(f"Your score is {st.session_state.score}/{len(st.session_state.questions)}")

    # Show save button only after submission and only once
    if st.session_state.show_save_button:
        if st.button("Save Score to Database"):
            save_score(st.session_state.student_name, st.session_state.score)
            st.success("Your score has been successfully saved!")
            st.session_state.show_save_button = False  # Hide after saving

    if st.button("View All Scores (Admin)"):
        scores = view_scores()
        st.table(scores)

if __name__ == "__main__":
    main()
