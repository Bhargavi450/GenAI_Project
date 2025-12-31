import streamlit as st
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import os
from datascraping import get_driver

load_dotenv()
driver=get_driver()

st.title("SUNBEAM ASSISTANT")

with st.sidebar:
    if st.button("ChatBot", width="stretch"):
        st.session_state.page="home"
    if st.button("Internship", width="stretch"):
        st.session_state.page="internship"
    if st.button("Courses", width="stretch"):
        st.session_state.page="courses"
    if st.button("About Us", width="stretch"):
        st.session_state.page="about_us"
    if st.button("Contact Us", width="stretch"):
        st.session_state.page="contact_us"

# SESSION STATE INIT
if "messages" not in st.session_state:
    st.session_state.messages = []

if "page" not in st.session_state:
    st.session_state.page="home"


@tool
def internship_info(expression: str) -> str:
    """
    Returns internship-related information in short bullet points.
    """
    try:
        file = read_file_content(
            r"E:/GIT Repos/GenAI_Project/datascraping.txt"
        )

        llm_input = f"""
        Data:
        {file}

        Question:
        {expression}

        Instructions:
        - Give 3–4 bullet points.
        - Use ONLY the data above.
        - Give Specific points for example 
           Course name: ...
           Fees: ...
           Batch: ...
           Starting date: ...
        """

        output = llm.invoke(llm_input)
        return output.content

    except Exception:
        return "Error: Information not found!"



def read_file_content(filepath: str) -> str:
    with open(filepath, "r") as file:
        return file.read()
   

@tool
def read_file(filepath: str) -> str:
    """
    Reads a text file and returns its content.
    """
    return read_file_content(filepath)



# MODEL
llm = init_chat_model(
    model="google/gemma-3-4b",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="non-needed"
)


# AGENT
agent = create_agent(
    model=llm,
    tools=[
        internship_info,
        read_file
    ],
    system_prompt="You are a helpful assistant. Answer in short."
)


# CHAT UI 
if st.session_state.page == "home":
    user_input = st.chat_input("Ask Anything...")

    if user_input:

        # store user message
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # invoke agent with full conversation history
        result = agent.invoke({
            "messages": st.session_state.messages
        })

        llm_output = result["messages"][-1]

        # store assistant response
        st.session_state.messages.append(
            {"role": "assistant", "content": llm_output.content}
        )

    #  DISPLAY CHAT HISTORY
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])



elif st.session_state.page=="internship":
    data1=read_file_content(r"E:/GIT Repos/GenAI_Project/internship.txt")
    st.write(data1)

elif st.session_state.page=="courses":
    data2=read_file_content(r"E:/GIT Repos/GenAI_Project/courses.txt")
    st.write(data2)

elif st.session_state.page=="about_us":
    data3=read_file_content(r"E:/GIT Repos/GenAI_Project/about.txt")
    st.write(data3)

elif st.session_state.page=="contact_us":
    data4=read_file_content(r"E:/GIT Repos/GenAI_Project/contact.txt")
    st.write(data4)