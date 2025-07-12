import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.ai_client import OllamaClient
from core.personality import PersonalityLoader

st.set_page_config(
    page_title="Bliss",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_client" not in st.session_state:
    st.session_state.ai_client = OllamaClient()
if "session_id" not in st.session_state:
    st.session_state.session_id = "default"
if "current_personality" not in st.session_state:
    st.session_state.current_personality = "default"


with st.sidebar:
    st.title("🤖 Bliss Settings")

    personalities = st.session_state.ai_client.get_available_personalities()
    selected_personality = st.selectbox(
        "Choose Personality",
        personalities,
        index=personalities.index(st.session_state.current_personality) if st.session_state.current_personality in personalities else 0
    )

    if selected_personality != st.session_state.current_personality:
        st.session_state.current_personality = selected_personality
        greeting = st.session_state.ai_client.get_greeting(selected_personality)
        st.session_state.messages = [{"role": "assistant", "content": greeting}]

    st.subheader("Session Management")
    new_session_id = st.text_input("Session ID: ", value=st.session_state.session_id)

    if st.button("New Session"):
        st.session_state.session_id = new_session_id if new_session_id else "default"
        st.session_state.messages = []
        greeting = st.session_state.ai_client.get_greeting(st.session_state.current_personality)
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    if st.button("Clear Conversation"):
        st.session_state.ai_client.clear_conversation_memory(st.session_state.session_id)
        st.session_state.messages = []
        greeting = st.session_state.ai_client.get_greeting(st.session_state.current_personality)
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    conv_count = st.session_state.ai_client.get_conversation_count(st.session_state.session_id)
    st.metric("Conversations", conv_count)

    personality_info = st.session_state.ai_client.get_current_personality_info()
    if personality_info:
        st.subheader("Current Personality")
        st.write(f"**Name:** {personality_info.get('name', 'Unknown')}")
        st.write(f"**Age:** {personality_info.get('age', 'Unknown')}")
        st.write(f"**Gender:** {personality_info.get('gender', 'Unknown')}")
        st.write(f"**Sexuality:** {personality_info.get('sexuality', 'Unknown')}")
        st.write(f"**Description:** {personality_info.get('description', 'No description')}")

    
st.title("💬 BLISS")

if not st.session_state.messages:
    greeting = st.session_state.ai_client.get_greeting(st.session_state.current_personality)
    st.session_state.messages.append({"role": "assistant", "content": greeting})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.ai_client.generate_response(
                    user_input=prompt,
                    personality_name=st.session_state.current_personality,
                    session_id=st.session_state.session_id,
                    context_limit=5
                )
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("Bliss is powered by Ollama")