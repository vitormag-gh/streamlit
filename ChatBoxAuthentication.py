# -*- coding: utf-8 -*-
"""
Created on Mon Aug  4 20:31:14 2025

@author: riskf
"""

import streamlit as st
import json
import tempfile
import os
from google import genai
from google.genai import types

# --- STEP 1: Authentication setup ---
# Robust session state initialization
for key in ("username", "pwd", "pwd_correct", "form_submitted"):
    if key not in st.session_state:
        st.session_state[key] = "" if key in ("username", "pwd") else False

# Function to check login
def check_login():
    st.session_state["form_submitted"] = True
    users = st.secrets.get("users", {})
    if users.get(st.session_state["username"]) == st.session_state["pwd"]:
        st.session_state["pwd_correct"] = True
        st.session_state["pwd"] = ""  # clear password
    else:
        st.session_state["pwd_correct"] = False

# Function to logout
def logout():
    for key in ("username", "pwd", "pwd_correct", "form_submitted", "chat_history", "user_input"):
        st.session_state[key] = "" if key in ("username", "pwd", "user_input") else False

# Function to display login form
def display_login_form():
    with st.form("login_form"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="pwd")
        st.form_submit_button("Login", on_click=check_login)

# --- STEP 2: If not logged in, show login form ---
if not st.session_state["pwd_correct"]:
    st.title("🔐 Login Required")
    display_login_form()
    if st.session_state["form_submitted"] and not st.session_state["pwd_correct"]:
        st.error("Invalid username or password.")
    st.stop()

# --- STEP 3: Authenticated — continue with chat app ---

# App title
st.title("🛍️ Gemini Return Policy Chatbot")
st.button("🚪 Logout", on_click=logout)

# --- Google Gemini Setup ---
# Load Google Service Account from secrets
service_account_info = dict(st.secrets["google_service_account"])

# Save service account JSON to a temporary file
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp_file:
    json.dump(service_account_info, tmp_file)
    tmp_file_path = tmp_file.name

# Set environment variable for authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path

# Initialize Gemini client
client = genai.Client(
    vertexai=True,
    project=service_account_info["project_id"],
    location="global"
)

# --- Session state: chat history ---
if "chat_history" not in st.session_state or not st.session_state["chat_history"]:
    st.session_state.chat_history = [
        types.Content(role="user", parts=[types.Part.from_text(text="""
You are a customer support bot in charge of return policy.
Items can only be returned if the item was purchased within the last 30 days and is unused.
Ask the customer follow-up questions to determine if their item can be returned or not.
Make sure to confirm that the item is BOTH unused and has been purchased in the last 30 days.
""")]),
        types.Content(role="model", parts=[types.Part.from_text(text="Thank you for contacting customer support. How can I assist you today?")])
    ]

# --- User input ---
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- Chat form ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submitted = st.form_submit_button("Send")

# --- On message sent ---
if submitted and user_input:
    st.session_state.chat_history.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_input)])
    )

    # Gemini config
    config = types.GenerateContentConfig(
        temperature=0.3,
        top_p=1,
        max_output_tokens=500,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
        ],
        thinking_config=types.ThinkingConfig(thinking_budget=-1)
    )

    # Call Gemini API
    response_chunks = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=st.session_state.chat_history,
        config=config
    )

    # Build response text
    response_text = ''
    for chunk in response_chunks:
        if chunk.text:
            response_text += chunk.text

    # Show response
    st.markdown(f"**🤖 Bot:** {response_text}")

    # Store bot response
    st.session_state.chat_history.append(
        types.Content(role="model", parts=[types.Part.from_text(text=response_text)])
    )

# --- Show conversation history ---
st.markdown("---")
st.subheader("Conversation History")
for msg in st.session_state.chat_history:
    role = "🧑 You" if msg.role == "user" else "🤖 Bot"
    st.markdown(f"**{role}:** {msg.parts[0].text}")
