import streamlit as st
import tempfile

from services.text_service import text_input_to_text
from services.image_service import image_to_text
from services.audio_service import audio_to_text
from services.video_service import video_to_text
from services.mcq_service import generate_mcq
from services.document_service import document_to_text
from services.url_service import scrape_url_to_text

# =======================
# Streamlit Config
# =======================
st.set_page_config(page_title="MCQ Generator", layout="centered")
st.title("AI-Powered Smart Quiz")

# =======================
# Session State Init
# =======================
defaults = {
    "page": "home",
    "mcqs": None,
    "user_answers": {},
    "quiz_generated": False,
    "quiz_submitted": False,
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# =======================
# Navigation
# =======================
def go_to(page):
    st.session_state.page = page
    st.session_state.mcqs = None
    st.session_state.user_answers = {}
    st.session_state.quiz_generated = False
    st.session_state.quiz_submitted = False
    st.rerun()

# =======================
# Helpers
# =======================
def collect_input_text():
    input_type = st.selectbox(
        "Select Input Type",
        ["Text", "Image", "Audio", "Video", "Document", "URL"]
    )

    extracted_text = ""

    if input_type == "Text":
        extracted_text = text_input_to_text(
            st.text_area("Enter text", height=200)
        )

    elif input_type == "URL":
        url = st.text_input("Enter URL")
        if url:
            extracted_text = scrape_url_to_text(url)

    else:
        uploaded_file = st.file_uploader(
            f"Upload {input_type}",
            type=["pdf", "docx"] if input_type == "Document" else None
        )

        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                file_path = tmp.name

            if input_type == "Image":
                extracted_text = image_to_text(file_path)
            elif input_type == "Audio":
                extracted_text = audio_to_text(file_path)
            elif input_type == "Video":
                extracted_text = video_to_text(file_path)
            elif input_type == "Document":
                extracted_text = document_to_text(file_path, uploaded_file.name)

    return extracted_text

def resolve_correct_answers(q):
    correct_raw = q.get("correct", [])
    options = q.get("options", {})

    # Already a list
    if isinstance(correct_raw, list):
        return set([k for k in correct_raw if k in options])

    # Otherwise fallback for string
    raw = str(correct_raw).strip()
    if "," in raw:
        parts = [p.strip() for p in raw.split(",")]
    else:
        parts = [raw]

    correct_keys = set()
    for part in parts:
        if part in options:
            correct_keys.add(part)
        else:
            for k, v in options.items():
                if v.strip().lower() == part.lower():
                    correct_keys.add(k)

    if not correct_keys and options:
        correct_keys.add(list(options.keys())[0])

    return correct_keys

# =======================
# HOME PAGE
# =======================
def render_home():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Create Quiz", use_container_width=True):
            go_to("create")

        if st.button("🧪 Attempt Quiz", use_container_width=True):
            go_to("attempt")

# =======================
# CREATE QUIZ PAGE
# =======================
def render_create():
    st.subheader("📝 Create Quiz")

    if st.button("⬅ Back to Home"):
        go_to("home")

    num_q = st.slider("Number of Questions", 1, 10, 5)

    text = collect_input_text()

    if st.button("Generate MCQs") and text.strip():
        with st.spinner("Generating MCQs..."):
            mcqs = generate_mcq(text, num_q)

        for q_id, q in mcqs.items():
            st.markdown(f"### Q{q_id}. {q['mcq']}")
            for opt, val in q["options"].items():
                st.write(f"{opt}) {val}")

            correct_keys = resolve_correct_answers(q)
            correct_text = ", ".join(q["options"][k] for k in correct_keys)

            st.success(f"Correct Answer(s): {correct_text}")
            st.write(f"Explanation: {q.get('explanation')}")

# =======================
# ATTEMPT QUIZ PAGE
# =======================
def render_attempt():
    st.subheader("🧪 Attempt Quiz")

    if st.button("⬅ Back to Home"):
        go_to("home")

    num_q = st.slider("Number of Questions", 1, 10, 5)

    # Generate quiz if not already
    if not st.session_state.quiz_generated:
        text = collect_input_text()

        if st.button("Generate Quiz") and text.strip():
            with st.spinner("Preparing Quiz..."):
                st.session_state.mcqs = generate_mcq(text, num_q)
                st.session_state.quiz_generated = True
                st.session_state.quiz_submitted = False
                st.session_state.user_answers = {}
                st.rerun()
        return

    mcqs = st.session_state.mcqs

    with st.form("quiz_form"):
        for q_id, q in mcqs.items():
            st.markdown(f"#### Q{q_id}. {q['mcq']}")
            correct_keys = resolve_correct_answers(q)

            # MULTI-CORRECT → CHECKBOX
            if len(correct_keys) > 1:
                if q_id not in st.session_state.user_answers:
                    st.session_state.user_answers[q_id] = set()

                selected = st.session_state.user_answers[q_id]
                st.markdown("Select all that apply")
                for opt_key, opt_val in q["options"].items():
                    checked = st.checkbox(
                        opt_val,
                        key=f"q_{q_id}_{opt_key}",
                        value=opt_key in selected
                    )
                    if checked:
                        selected.add(opt_key)
                    else:
                        selected.discard(opt_key)

                st.session_state.user_answers[q_id] = selected

            # SINGLE-CORRECT → RADIO
            else:
                if q_id not in st.session_state.user_answers:
                    st.session_state.user_answers[q_id] = list(q["options"].keys())[0]

                choice = st.radio(
                    "Choose one option",
                    options=list(q["options"].keys()),
                    format_func=lambda k: q["options"][k],
                    index=list(q["options"].keys()).index(st.session_state.user_answers[q_id]),
                    key=f"q_{q_id}"
                )

                st.session_state.user_answers[q_id] = choice

        submitted = st.form_submit_button("Submit Quiz")

    # =======================
    # Check if all questions are answered
    # =======================
    all_answered = True
    for q_id, q in mcqs.items():
        ans = st.session_state.user_answers.get(q_id)
        if isinstance(ans, set) and len(ans) == 0:
            all_answered = False
            break
        if ans is None:
            all_answered = False
            break

    if submitted:
        if not all_answered:
            st.warning("Please answer all questions before submitting.")
        else:
            st.session_state.quiz_submitted = True

    # =======================
    # Show Results
    # =======================
    if st.session_state.quiz_submitted:
        score = 0
        st.subheader("📊 Quiz Results")

        for q_id, q in mcqs.items():
            correct_keys = resolve_correct_answers(q)
            user_answer = st.session_state.user_answers[q_id]

            st.markdown(f"### Q{q_id}. {q['mcq']}")

            if isinstance(user_answer, set):
                user_text = ", ".join(q["options"][k] for k in user_answer)
                correct_text = ", ".join(q["options"][k] for k in correct_keys)

                st.write(f"🧑 Your Answer(s): **{user_text}**")
                st.write(f"✅ Correct Answer(s): **{correct_text}**")

                if user_answer == correct_keys:
                    score += 1
                    st.success("Correct ✅")
                else:
                    st.error("Incorrect ❌")

            else:
                st.write(f"🧑 Your Answer: **{q['options'][user_answer]}**")
                correct_key = list(correct_keys)[0]
                st.write(f"✅ Correct Answer: **{q['options'][correct_key]}**")

                if user_answer == correct_key:
                    score += 1
                    st.success("Correct ✅")
                else:
                    st.error("Incorrect ❌")

            st.write(f"Explanation: {q.get('explanation')}")
            st.divider()

        st.info(f"Final Score: {score} / {len(mcqs)}")

# =======================
# ROUTER
# =======================
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "create":
    render_create()
elif st.session_state.page == "attempt":
    render_attempt()
