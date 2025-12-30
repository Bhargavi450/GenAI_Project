import streamlit as st

st.set_page_config(layout="wide")
 
if "page" not in st.session_state:
    st.session_state.page = "home"
 
col1, col2, col3 = st.columns([8, 1, 1])

with col2:
    if st.button("Sign In"):
        st.session_state.page = "signin"

with col3:
    if st.button("Login"):
        st.session_state.page = "login"

st.markdown("---")
 
if st.session_state.page == "home":
    st.title("Sunbeam Internship")
 
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
        else:
            st.error("Please fill all fields")
 
elif st.session_state.page == "login":
    st.title("Login")

    with st.form("LoginForm"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if email and password:
            st.success("Login Successful")
        else:
            st.error("Please enter email and password")
