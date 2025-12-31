import streamlit as st
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

# ---------------- CONFIG ----------------
load_dotenv()

BASE_PATH = "E:/GIT Repos/GenAI_Project"

st.set_page_config(
    page_title="SUNBEAM ASSISTANT",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align: center;'>🎓 SUNBEAM ASSISTANT</h1>",
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 📌 Navigation")
    if st.button("💬 ChatBot", use_container_width=True):
        st.session_state.page = "home"
    if st.button("📊 Internship", use_container_width=True):
        st.session_state.page = "internship"
    if st.button("📘 Courses", use_container_width=True):
        st.session_state.page = "courses"
    if st.button("🏫 About Us", use_container_width=True):
        st.session_state.page = "about_us"
    if st.button("📞 Contact Us", use_container_width=True):
        st.session_state.page = "contact_us"

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- MODEL ----------------
llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed"
)

# ---------------- FILE HELPERS ----------------
def read_file_content(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def answer_from_file(filepath: str, question: str) -> str:
    data = read_file_content(filepath)

    prompt = f"""
You are a SUNBEAM Institute assistant.

IMPORTANT RULES:
- The DATA below is already available to you.
- DO NOT ask the user to provide files or data.
- DO NOT mention tools, scraping, or file access.
- Answer ONLY using the information present in the DATA section.
- If the answer is not present, say:
  "The requested information is not available in the provided data."

DATA:
{data}

QUESTION:
{question}

Answer in professional bullet points.
"""

    return llm.invoke(prompt).content

# ======================================================
# ======================= CHAT =========================
# ======================================================
if st.session_state.page == "home":
    st.markdown("### 💬 Ask anything about Sunbeam")

    user_input = st.chat_input("Ask about internships, courses, contact details...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        text = user_input.lower()

        if "internship" in text:
            reply = answer_from_file(
                f"{BASE_PATH}/internship.txt",
                user_input
            )

        elif "course" in text or "modular" in text:
            reply = answer_from_file(
                f"{BASE_PATH}/courses.txt",
                user_input
            )

        elif "about" in text or "sunbeam" in text:
            reply = answer_from_file(
                f"{BASE_PATH}/about.txt",
                user_input
            )

        elif "contact" in text or "phone" in text or "email" in text:
            reply = answer_from_file(
                f"{BASE_PATH}/contact.txt",
                user_input
            )

        else:
            reply = answer_from_file(
                f"{BASE_PATH}/datascraping_complete.txt",
                user_input
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ======================================================
# ================= INTERNSHIP =========================
# ======================================================
elif st.session_state.page == "internship":
    st.markdown("## 📊 Internship Programs")
    st.write(read_file_content(f"{BASE_PATH}/internship.txt"))

# ======================================================
# ================= COURSES =============================
# ======================================================
elif st.session_state.page == "courses":
    st.markdown("## 📘 Courses Offered")
    st.write(read_file_content(f"{BASE_PATH}/courses.txt"))

# ======================================================
# ================= ABOUT ===============================
# ======================================================
elif st.session_state.page == "about_us":
    st.markdown("## 🏫 About Sunbeam")
    st.write(read_file_content(f"{BASE_PATH}/about.txt"))

# ======================================================
# ================= CONTACT =============================
# ======================================================
elif st.session_state.page == "contact_us":
    st.markdown("## 📞 Contact Information")
    st.write(read_file_content(f"{BASE_PATH}/contact.txt"))
