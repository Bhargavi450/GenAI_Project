import streamlit as st
from langchain.chat_models import init_chat_model

st.set_page_config(layout="wide")
 
if "page" not in st.session_state:
    st.session_state.page = "home"

if "login" not in st.session_state:
    st.session_state.login = False
 
col1, col2, col3, col4 = st.columns([6, 1, 1, 1])


with col3:
    if st.button("Sign In", type="primary", width="stretch"):
        st.session_state.page = "signin"

with col4:
    if st.button("Login", type="primary", width="stretch"):
        st.session_state.page = "login"

st.markdown("---")
 
if st.session_state.page == "home":
    st.title("Sunbeam Internship")
    st.subheader("All you want to learn about Internships that sunbeam is offering!")
 
elif st.session_state.page == "signin":
    st.title("Sign In")

    with st.form("SignInForm"):
        email = st.text_input("Email")
        name = st.text_input("Name")
        phone = st.text_input("Phone Number")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")


    if submit:
        if email and name and phone and password:
            st.success("Sign In Successful")
            st.session_state.login=True
            st.session_state.page="chatbot"
        else:
            st.error("Please fill all fields")
            st.session_state.login=False
 
elif st.session_state.page == "login":
    st.title("Login")

    with st.form("LoginForm"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if email and password:
            st.success("Login Successful")
            st.session_state.login=True
            st.session_state.page="chatbot"
        else:
            st.error("Please enter email and password")
            st.session_state.login=False
            
elif st.session_state.page=="chatbot":
    st.title("SUNBEAM CHATBOT")

    llm = init_chat_model(
        model="google/gemma-3-4b",
        model_provider="openai",
        base_url="http://127.0.0.1:1234/v1",
        api_key="dummy-key"
    )

    # Initialize conversation history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # User input
    user_input = st.chat_input("Ask anything:")

    if user_input:
        # Add user message to history
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # Invoke LLM with full conversation history
        response = llm.invoke(st.session_state.messages)

        # Add assistant response to history
        st.session_state.messages.append(
            {"role": "assistant", "content": response.content}
        )

    # Display chat history (skip system message)
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

