import streamlit as st
import google.generativeai as genai
import re
import random
import os

# Set up Google Gemini API key (Replace with your actual API key)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

## Function to generate a multiple-choice coding challenge
def generate_single_challenge(topic):
    prompt = (
        f"Generate a beginner-friendly multiple-choice coding challenge for {topic}. "
        "Format response exactly as:\n"
        "Question: <your question>\n"
        "Choices:\n"
        "a) <option1>\n"
        "b) <option2>\n"
        "c) <option3>\n"
        "d) <option4>\n"
        "Answer: <correct choice letter>"
    )

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # ✅ Debugging: Print raw API response
        if response:
            print("Raw API Response:", response)

        # ✅ Extract response text correctly
        response_text = getattr(response, "text", "").strip() if hasattr(response, "text") else ""
        if not response_text:
            return None, None, None  # No valid response received

        print("Processed Response Text:", response_text)  # Debugging output

        # ✅ Use regex to extract question, choices, and answer
        question_match = re.search(r"Question:\s*(.*?)\s*Choices:", response_text, re.DOTALL)
        choices_match = re.findall(r"[a-d]\)\s*(.*)", response_text)
        answer_match = re.search(r"Answer:\s*([a-dA-D])", response_text)

        if question_match and choices_match and answer_match and len(choices_match) == 4:
            question = question_match.group(1).strip()
            correct_choice_letter = answer_match.group(1).lower()
            choices = [choice.strip() for choice in choices_match]

            # Get the correct answer text before shuffling
            correct_answer_text = choices["abcd".index(correct_choice_letter)]

            # Shuffle choices while keeping track of the correct answer
            random.shuffle(choices)

            return question, choices, correct_answer_text
        else:
            print("❌ Extraction Failed. Check API Response Format.")
            return None, None, None

    except Exception as e:
        print(f"❌ API Error: {e}")
        return None, None, None


# Streamlit App
st.title("🛡️ Gamified Learning Platform 🏆")
st.sidebar.header("🎯 Choose Your Learning Path")

# Learning paths
learning_paths = ["Python", "AI/ML", "SQL", "Data Science"]
selected_path = st.sidebar.radio("Select a topic:", learning_paths)

# Initialize session state variables if not already set
if "current_question" not in st.session_state or st.session_state.get("current_path") != selected_path:
    st.session_state["current_question"], st.session_state["choices"], st.session_state["correct_answer"] = generate_single_challenge(selected_path)
    st.session_state["current_path"] = selected_path
    st.session_state["completed"] = 0
    st.session_state["feedback"] = ""
    st.session_state["correct"] = False

# Display challenge
st.subheader(f"{selected_path} Challenge")
if st.session_state["current_question"]:
    st.write(f"📝 Challenge {st.session_state['completed'] + 1}: {st.session_state['current_question']}")

    # Show multiple-choice options
    answer = st.radio("Select your answer:", st.session_state["choices"], key="answer_choice")

    if st.button("Submit Answer"):
        correct_answer = st.session_state["correct_answer"]

        if answer == correct_answer:
            st.session_state["feedback"] = "✅ Correct! Click 'Next Question' to continue."
            st.session_state["correct"] = True
        else:
            st.session_state["feedback"] = f"❌ Incorrect! Try again."

    st.write(st.session_state["feedback"])

    # Show "Next Question" button only if the answer is correct
    if st.session_state["correct"]:
        if st.button("Next Question"):
            st.session_state["completed"] += 1
            st.session_state["feedback"] = ""
            st.session_state["correct"] = False
            st.session_state["current_question"], st.session_state["choices"], st.session_state["correct_answer"] = generate_single_challenge(selected_path)
            st.rerun()

else:
    st.error("⚠️ Failed to load a challenge. Please try again.")

# XP & Level System
st.sidebar.subheader("📊 Player Stats")
xp = st.session_state["completed"] * 10
st.sidebar.write(f"🌟 XP: {xp}")
level = xp // 100 + 1
st.sidebar.write(f"🏅 Level: {level}")

st.sidebar.write("🔓 Unlock more topics by leveling up!")

