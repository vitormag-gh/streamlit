import streamlit as st

# --- STEP 1: Initialize session state safely ---
# Each key is initialized individually to avoid KeyError
if "username" not in st.session_state:
    st.session_state["username"] = ""

if "pwd" not in st.session_state:
    st.session_state["pwd"] = ""

if "pwd_correct" not in st.session_state:
    st.session_state["pwd_correct"] = False

if "form_submitted" not in st.session_state:
    st.session_state["form_submitted"] = False

# --- STEP 2: Function to check login credentials ---
def check_login():
    st.session_state["form_submitted"] = True
    users = st.secrets.get("users", {})  # Load users from secrets.toml

    # Verify entered username and password
    if users.get(st.session_state["username"]) == st.session_state["pwd"]:
        st.session_state["pwd_correct"] = True
        st.session_state["pwd"] = ""  # Clear password
    else:
        st.session_state["pwd_correct"] = False

# --- STEP 3: Logout function resets all session state variables ---
def logout():
    st.session_state["username"] = ""
    st.session_state["pwd"] = ""
    st.session_state["pwd_correct"] = False
    st.session_state["form_submitted"] = False

# --- STEP 4: Login form UI ---
def display_login_form():
    with st.form("login_form"):
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="pwd")
        st.form_submit_button("Login", on_click=check_login)

# --- STEP 5: Main logic for login and access control ---
if not st.session_state["pwd_correct"]:
    display_login_form()

    if st.session_state["form_submitted"]:
        st.error("Invalid username or password.")
else:
    st.success(f"✅ Welcome, {st.session_state['username']}!")
    st.button("Logout", on_click=logout)

    # Place your protected app content below
    st.write("🔒 This is your protected app content.")
