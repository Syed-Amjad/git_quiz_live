import os
import streamlit as st
import sqlite3
import re

# Groq API
from groq import Groq

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
# Groq Quiz Question Generation
# ------------------------------------------------------------------------------
def generate_questions(client):
    """Generates a set of Git questions using Groq API."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Create 20 multiple-choice questions with 4 options each about Git (introduction, add, commit, stash, branch, merge, push, pull, pull requests) and identify the correct answer for each."
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct"

        )
        response = chat_completion.choices[0].message.content

        # Split questions by number
        question_blocks = re.split(r'\n[0-9]+\.\s', response)
        questions = []

        for block in question_blocks[1:]:
            lines = block.strip().splitlines()
            question = lines[0].strip()
            options = []
            answer = ""

            for line in lines[1:]:
                if re.match(r'[a-d]\)', line):
                    options.append(line[3:].strip())  # Strip "a) " etc.
                elif line.startswith("Answer:") or line.startswith("Correct Answer:"):
                    answer = line.split(':')[1].strip()

            if question and options and answer:
                questions.append({"question": question, "options": options, "answer": answer})

        return questions

    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []


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

    # API key
    if "GROQ_API_KEY" not in st.secrets:
        st.error("Groq API key not configured in Streamlit secrets.")
        st.stop()

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=GROQ_API_KEY)

    # Student enters their name first
    student_name = st.text_input("Enter your name:")

    if not student_name:
        st.error("Please enter your name to proceed.")
        return

    st.write(f"Hello, {student_name}! Let's start the quiz.")

    if st.button("Start Quiz with AI-generated questions"):
        questions = generate_questions(client)
        if questions:
            st.session_state['questions'] = questions
        else:
            st.error("Unable to generate questions. Please try again later.")
            return

    if 'questions' in st.session_state:
        questions = st.session_state['questions']

        score = 0

        answers = []

        for idx, q in enumerate(questions, 1):
            st.write(f"Question {idx}. {q['question']}")

            answer = st.radio("Select your answer", q['options'], key=str(idx))
            answers.append(answer)

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
