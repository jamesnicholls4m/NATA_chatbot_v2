import streamlit as st
import openai
import pandas as pd

# Show title and description.
st.title("🔍 Excel Search Chatbot")
st.write(
    "This chatbot searches an Excel file stored in a GitHub repository and uses OpenAI's GPT-3.5 model to generate responses based on the queried data. "
    "Make sure to configure your OpenAI API key in the Streamlit secrets section."
)

# Retrieve the OpenAI API Key securely stored in Streamlit secrets.
openai_api_key = st.secrets["openai_api_key"]

# Initialize OpenAI with the API key.
openai.api_key = openai_api_key

# Define the GitHub URL of the Excel file.
excel_url = 'https://raw.githubusercontent.com/your-repo/your-repo/main/your-excel-file.xlsx'

# Load Excel file.
@st.cache
def load_excel(url):
    return pd.read_excel(url)

data = load_excel(excel_url)

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field for the user to enter a message.
prompt = st.chat_input("What is up?")
if prompt:
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search the Excel file based on the user's question.
    search_result = data[data.apply(lambda row: row.astype(str).str.contains(prompt, case=False).any(), axis=1)]

    # Convert the search result to a string.
    search_result_str = search_result.to_string(index=False)

    # Generate a response using the OpenAI API, including the search result.
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"User asked: {prompt}\nExcel Data:\n{search_result_str}\nGenerate a response for the user.",
        max_tokens=150
    ).choices[0].text.strip()

    # Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(response)

    # Store the response in session state.
    st.session_state.messages.append({"role": "assistant", "content": response})
