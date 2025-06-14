import streamlit as st
import os
import sqlite3
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

    # Initialize Groq client
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Create 20 multiple-choice questions about Git with 4 options each and indicate the correct answer in your response"}
            ],
            model='mixtral-8x7b'  # or whatever supported by your API
        )
        generated_questions = chat_completion.choices[0].message.content

    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return

    st.success("Questions generated! Please answer them below:")

    # Parsing the generated questions
    # This is a simplified parsing — you may need to adjust this depending on the format of the API response
    lines = generated_questions.splitlines()
    questions = []
    temp = {"question": "", "options": [], "answer": ""}
    for line in lines:
        line = line.strip()
        if line.startswith("Question"):
            if temp["question"]:
                questions.append(temp.copy())  # Store previous
                temp = {"question": "", "options": [], "answer": ""}
            temp["question"] = line
        elif line.startswith("A.") or line.startswith("B.") or line.startswith("C.") or line.startswith("D."):
            temp["options"].append(line)
        elif line.startswith("Answer:"):
            temp["answer"] = line.split("Answer:")[-1].strip()
    if temp["question"]:
        questions.append(temp.copy())  # Store last one

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
