import pandas as pd
import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(BASE_DIR, "data", "words")

files = os.listdir(path)

# Read in data and add 'all' as subcategory 
data = pd.DataFrame()
for f in files:
    dat =  pd.read_csv(os.path.join(path, f), sep="\t")
    dat = pd.concat(
                    [dat, dat.assign(cat1="all")],
                    ignore_index=True
                )
    print(dat.head())
    data = pd.concat([data, dat], ignore_index = True)

# select category
cat = st.selectbox(
    "Main category",
    sorted(data["cat"].unique())
)

subcat = st.selectbox(
    "Subcategory",
    sorted(
        data.loc[data["cat"] == cat, "cat1"].unique()
    )
)

# filter to selected categories
filtered_data = data[
    (data["cat"] == cat) &
    (data["cat1"] == subcat)
]


# display N words
st.write(f"Words available: {len(filtered_data)}")

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
        "italian": selected["italian"],
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
# CHECK ANSWER
# -------------------------

if not st.session_state.checked:

    if st.button("Check"):

        st.session_state.answer = answer
        st.session_state.checked = True

        # Normalize both answers
        user_answer = answer.strip().lower()
        correct_answer = word["italian"].strip().lower()

        if user_answer == correct_answer:

            st.session_state.feedback = "correct"

            # Remove the answered word from the pool.
            #
            # We identify it by its actual English/Italian values
            # rather than relying on the DataFrame index.
            mask = ~(
                (st.session_state.quiz_pool["english"] == word["english"])
                &
                (st.session_state.quiz_pool["italian"] == word["italian"])
            )

            st.session_state.quiz_pool = (
                st.session_state.quiz_pool.loc[mask].copy()
            )

        else:

            st.session_state.feedback = "incorrect"

        st.rerun()


# -------------------------
# DISPLAY FEEDBACK
# -------------------------

if st.session_state.feedback == "correct":

    st.success("Correct!")

elif st.session_state.feedback == "incorrect":

    st.error(
        f"Incorrect. Correct answer: {word['italian']}"
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
