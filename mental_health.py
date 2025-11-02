import streamlit as st
import ollama
import base64
import os

st.set_page_config(page_title="Mental Health Chatbot", layout="centered")

def get_base64(background):
    try:
        with open(background, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

bin_str = get_base64("background.png")

if bin_str:
    st.markdown(f"""
        <style>
            .main {{
                background-image: url("data:image/png;base64,{bin_str}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            h1, h3 {{
                text-align: center;
                color: #4B8BBE;
            }}
            .stButton>button {{
                background-color: #4B8BBE;
                color: white;
                border-radius: 10px;
            }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.warning("Background image not found, continuing without background image.")

st.markdown("<h1>🧘 Mental Health Support Agent</h1>", unsafe_allow_html=True)

# Initialize conversation history with a max length limit
MAX_HISTORY_LENGTH = 20
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []

def trim_history():
    if len(st.session_state['conversation_history']) > MAX_HISTORY_LENGTH:
        st.session_state['conversation_history'] = st.session_state['conversation_history'][-MAX_HISTORY_LENGTH:]

def generate_response(user_input):
    st.session_state['conversation_history'].append({"role": "user", "content": user_input})
    trim_history()
    try:
        response = ollama.chat(model="llama3.1:8b", messages=st.session_state['conversation_history'])
        ai_response = response['message']['content']
    except Exception:
        ai_response = "Sorry, I'm currently unable to respond. Please try again later."
    st.session_state['conversation_history'].append({"role": "assistant", "content": ai_response})
    trim_history()
    return ai_response

@st.cache_data(ttl=3600)  # Cache with expiration of 1 hour to allow refresh over time
def generate_affirmation():
    prompt = "Provide a positive affirmation to encourage someone who is feeling stressed or overwhelmed."
    try:
        response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception:
        return "Sorry, unable to generate affirmation right now."

@st.cache_data(ttl=3600)
def generate_meditation_guide():
    prompt = "Provide a 5-minute guided meditation script to help someone relax and reduce stress."
    try:
        response = ollama.chat(model="llama3.1:8b", messages=[{"role": "user", "content": prompt}])
        return response['message']['content']
    except Exception:
        return "Sorry, unable to generate meditation guide right now."

# Display conversation history
for msg in st.session_state['conversation_history']:
    role = "You" if msg['role'] == "user" else "AI"
    st.markdown(f"**{role}:** {msg['content']}")

user_message = st.text_input("How can I help you today?", key="user_input", label_visibility="visible")

if user_message:
    with st.spinner("Thinking..."):
        ai_response = generate_response(user_message)
        st.markdown(f"**AI:** {ai_response}")

col1, col2 = st.columns(2)

with col1:
    if st.button("Give me a positive Affirmation", key="affirmation_btn"):
        with st.spinner("Generating affirmation..."):
            affirmation = generate_affirmation()
            st.markdown(f"**Affirmation:** {affirmation}")

with col2:
    if st.button("Give me a guided Meditation", key="meditation_btn"):
        with st.spinner("Generating meditation guide..."):
            meditation_guide = generate_meditation_guide()
            st.markdown(f"**Guided Meditation:** {meditation_guide}")


st.markdown("""
---
⚠️ **Disclaimer:**  
This chatbot is not a substitute for professional mental health care.  
If you are in crisis or experiencing severe distress, please reach out to a licensed therapist or mental health helpline.
""")

