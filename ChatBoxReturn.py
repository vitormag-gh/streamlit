# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 18:58:40 2025

@author: riskf
"""
import streamlit as st
import json
import tempfile
import os
from google import genai
from google.genai import types

# Convert SecretsDict to native dict
service_account_info = dict(st.secrets["google_service_account"])

# Write it to a temp JSON file
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmp_file:
    json.dump(service_account_info, tmp_file)
    tmp_file_path = tmp_file.name

# --- Set env var for Google client to pick up ---
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp_file_path



# --- Initialize Gemini client ---
client = genai.Client(
    vertexai=True,
    project=service_account_info["project_id"],
    location="global"
)


# --- App title ---
st.title("🛍️ Gemini Return Policy Chatbot")

# --- Session state to track conversation ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text="""
You are a customer support bot in charge of return policy.
Items can only be returned if the item was purchased within the last 30 days and is unused.
Ask the customer follow-up questions to determine if their item can be returned or not.
Make sure to confirm that the item is BOTH unused and has been purchased in the last 30 days.
""")]
        ),
        types.Content(
            role="model",
            parts=[types.Part.from_text(text="Thank you for contacting customer support. How can I assist you today?")]
        )
    ]

# --- Input key workaround to avoid mutation error ---
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# --- Input form for message ---
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submitted = st.form_submit_button("Send")

# --- On Send button pressed ---
if submitted and user_input:
    # Add user message
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

    # Call Gemini
    response_chunks = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=st.session_state.chat_history,
        config=config
    )

    # Build response
    response_text = ''
    for chunk in response_chunks:
        if chunk.text:
            response_text += chunk.text

    # Show response
    st.markdown(f"**Bot:** {response_text}")
    
    # Add response to chat history
    st.session_state.chat_history.append(
        types.Content(role="model", parts=[types.Part.from_text(text=response_text)])
    )

# --- Show conversation history ---
st.markdown("---")
st.subheader("Conversation History")
for msg in st.session_state.chat_history:
    role = "🧑 You" if msg.role == "user" else "🤖 Bot"
    st.markdown(f"**{role}:** {msg.parts[0].text}")

