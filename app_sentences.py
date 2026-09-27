import pandas as pd
import streamlit as st
import os


path = r"C:\Users\roza0\Desktop\projects\italian_app\data\sentences\ita_clean.csv"
data = pd.read_csv(path, sep=",")

# select difficulty
level = st.selectbox(
    "Difficulty level",
    sorted(data["level"].unique())
)

k = st.number_input(
    label = "Number of words",
    min_value = 1,
    max_value = 1000,
    value = 15
)

# filter to selected categories
filtered_data = (
    data[data["level"] == level]
    .sample(n=k)
)


# Reset quiz when category changes
if "last_cat" not in st.session_state or st.session_state.last_cat != (cat, subcat):
    st.session_state.last_cat = (cat, subcat)
    st.session_state.quiz_pool = (
        filtered_data
        .sample(frac=1)
        .reset_index(drop=True)
    )
    st.session_state.feedback = None


if len(st.session_state.quiz_pool) == 0:
    st.success("Congratulations! You know all the words!")
    st.stop()


word = st.session_state.quiz_pool.iloc[0]

st.title("Italian Vocabulary Quiz")
st.header(word["english"])

answer = st.text_input("Italian")


if st.button("Check"):

    if answer.strip().lower() == word["italian"].strip().lower():
        st.session_state.feedback = "correct"

    else:
        st.session_state.feedback = "incorrect"


# Display feedback
if st.session_state.feedback == "correct":
    st.success("Correct!")

elif st.session_state.feedback == "incorrect":
    st.error(f"Incorrect. Correct answer: {word['italian']}")


# Only move on when clicking Next
if st.button("Next word"):

    st.session_state.quiz_pool = (
        st.session_state.quiz_pool.iloc[1:]
        .reset_index(drop=True)
    )

    st.session_state.feedback = None
    st.rerun()