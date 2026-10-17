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


# -------------------------
# QUIZ STATE INITIALIZATION
# -------------------------

# Reset quiz when category changes
if (
    "last_cat" not in st.session_state
    or st.session_state.last_cat != (cat, subcat)
):
    st.session_state.last_cat = (cat, subcat)

    # Create a fresh pool for this category
    st.session_state.quiz_pool = (
        filtered_data
        .reset_index(drop=True)
        .copy()
    )

    # Current question
    st.session_state.current_word = None

    # User's current answer
    st.session_state.answer = ""

    # Feedback state
    st.session_state.feedback = None

    # Whether the current question has been checked
    st.session_state.checked = False

# -------------------------
# FINISHED?
# -------------------------

if st.session_state.quiz_pool.empty:

    st.markdown(
        """
        <div style="
            text-align: center;
            margin-top: 30px;
            margin-bottom: 40px;
            color: #0066cc;
        ">
            <div style="
                font-size: 32px;
                font-weight: 700;
            ">
                Congratulations!
            </div>
            <div style="
                font-size: 32px;
                font-weight: 700;
            ">
                You know all the words!
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    <style>
    div.stButton {
        display: flex;
        justify-content: center;
    }
    div.stButton > button {
        width: 150px;
        color: #0066cc;
        background-color: white;
        border: 2px solid #0066cc;
        border-radius: 6px;
    }

    div.stButton > button:hover {
        color: white;
        background-color: #0066cc;
        border-color: #0066cc;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("Play again"):

        # Reset the quiz pool
        st.session_state.quiz_pool = (
            filtered_data
            .reset_index(drop=True)
            .copy()
        )

        # Reset the current question
        st.session_state.current_word = None
        st.session_state.answer = ""
        st.session_state.feedback = None
        st.session_state.checked = False

        # Reset progress
        st.session_state.quiz_pool_initial_size = len(
            st.session_state.quiz_pool
        )

        st.rerun()

    st.stop()


# -------------------------
# SELECT A NEW RANDOM WORD
# -------------------------

if st.session_state.current_word is None:

    # Pick one row randomly
    selected = st.session_state.quiz_pool.sample(1).iloc[0]

    # Store the actual word, NOT its DataFrame index
    st.session_state.current_word = {
        "english": selected["english"],
        "italian": selected["italian_clean"],
    }

    # Reset question state
    st.session_state.answer = ""
    st.session_state.feedback = None
    st.session_state.checked = False


# Get current word
word = st.session_state.current_word

# -------------------------
# DISPLAY QUESTION
# -------------------------

st.title("Italian Vocabulary Quiz")
st.header(word["english"])

# -------------------------
# ANSWER INPUT
# -------------------------

answer = st.text_input(
    "Italian",
    value=st.session_state.answer,
    disabled=st.session_state.checked,
)


# -------------------------
# NEXT WORD
# -------------------------

if st.session_state.checked:

    if st.button("Next word"):

        # Forget the current question
        st.session_state.current_word = None

        # Reset question state
        st.session_state.answer = ""
        st.session_state.feedback = None
        st.session_state.checked = False

        st.rerun()


# -------------------------
# QUIZ PROGRESS BAR
# -------------------------

# Total number of words at the start of this quiz
n_words_available = len(filtered_data)

# Number answered correctly
n_words_correct = (
    n_words_available - len(st.session_state.quiz_pool)
)

# Progress as a fraction between 0 and 1
progress = (
    n_words_correct / n_words_available
    if n_words_available > 0
    else 0
)

# Progress bar
st.markdown(
    f"""
    <div style="
        width: 100%;
        height: 10px;
        background-color: #bde3f4;
        border-radius: 5px;
        overflow: hidden;
        margin-top: 30px;
    ">
        <div style="
            width: {progress * 100}%;
            height: 100%;
            background-color: #1976d2;
            border-radius: 5px;
        ">
        </div>
    </div>

    <div style="
        text-align: center;
        margin-top: 6px;
        font-size: 14px;
    ">
        {n_words_correct} / {n_words_available} words learned
    </div>
    """,
    unsafe_allow_html=True
)
