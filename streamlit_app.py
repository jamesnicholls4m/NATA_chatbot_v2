import streamlit as st
import openai
import pandas as pd
import urllib.error

# Show title and description.
st.title("🔍 Excel Search Chatbot")
st.write(
    "This chatbot searches a CSV file stored in a GitHub repository and uses OpenAI's GPT-3.5 model to generate responses based on the queried data. "
    "Make sure to configure your OpenAI API key in the Streamlit secrets section."
)

# Retrieve the OpenAI API Key securely stored in Streamlit secrets.
openai_api_key = st.secrets["general"]["openai_api_key"]

# Initialize OpenAI with the API key.
openai.api_key = openai_api_key

# Define the GitHub URL of the CSV file.
csv_url = 'https://raw.githubusercontent.com/jamesnicholls4m/wordcloud-application/main/NATA%20A2Z%20List%20-%20August%202024%20-%20v1.csv'

# Load CSV file with error handling.
@st.cache_data
def load_csv(url):
    try:
        data = pd.read_csv(url)
        return data
    except urllib.error.HTTPError as e:
        st.error(f"HTTPError: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

data = load_csv(csv_url)

if data is None:
    st.stop()  # Stop the app if the data couldn't be loaded.

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field for the user to enter a message.
prompt = st.chat_input("Type your question here...")
if prompt:
    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Search the CSV file based on the user's question.
    search_result = data[data.apply(lambda row: row.astype(str).str.contains(prompt, case=False).any(), axis=1)]

    # Convert search result to a string.
    if not search_result.empty:
        search_result_str = search_result.to_string(index=False)
    else:
        search_result_str = "No relevant data found in the CSV file."

    # Generate a response using the OpenAI API, including the search result in the prompt.
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"User asked: {prompt}\nCSV Data:\n{search_result_str}\nGenerate a response for the user.",
        max_tokens=150
    ).choices[0].text.strip()

    # Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(response)

    # Store the response in session state.
    st.session_state.messages.append({"role": "assistant", "content": response})
