import streamlit as st
import sys
import os
import queue
import threading

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.ai_client import OllamaClient
from core.personality import PersonalityLoader
from voice.speech_to_text import create_speech_to_text
from voice.text_to_speech import create_text_to_speech

st.set_page_config(
    page_title="Bliss",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_client" not in st.session_state:
    st.session_state.ai_client = OllamaClient(model_name="qwen3:1.7b")
if "session_id" not in st.session_state:
    st.session_state.session_id = "default"
if "current_personality" not in st.session_state:
    st.session_state.current_personality = "default"
if "stt" not in st.session_state:
    st.session_state.stt = create_speech_to_text()
if "tts" not in st.session_state:
    st.session_state.tts = create_text_to_speech()
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True
if "auto_speak_responses" not in st.session_state:
    st.session_state.auto_speak_responses = False


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

    st.subheader("🎤 Voice Settings")

    stt_available = st.session_state.stt.is_microphone_available()
    tts_available = st.session_state.tts.is_available()

    st.session_state.voice_enabled = st.checkbox(
        "Enable Voice Features",
        value=st.session_state.voice_enabled and (stt_available and tts_available)
    )

    if st.session_state.voice_enabled:
        if stt_available:
            st.success("🎤 Microphone: Available")
        else:
            st.error("🎤 Microphone: Not available")
        
        if tts_available:
            st.success("🔊 Text-to-Speech: Available")
            
            st.session_state.auto_speak_responses = st.checkbox(
                "Auto-speak AI responses", 
                value=st.session_state.auto_speak_responses
            )

            with st.expander("TTS settings"):
                voices = st.session_state.tts.get_voices()
                if voices:
                    voice_names = [f"{v['name']}" for v in voices]
                    selected_voice_index = st.selectbox(
                        "voice:",
                        range(len(voice_names)),
                        format_func=lambda x: voice_names[x]
                    )
                    if st.button("Apply Voice"):
                        st.session_state.tts.set_voice(voices[selected_voice_index]['id'])
                        st.success("Voice updated!")
                
                speech_rate = st.slider("Speech Rate (WPM)", 50, 300, 180)
                speech_volume = st.slider("Volume", 0.0, 1.0, 0.8)

                st.session_state.tts.set_rate(speech_rate)
                st.session_state.tts.set_volume(speech_volume)

                if st.button("Test Voice"):
                    test_text = "Hello! This is a test of my voice"
                    st.session_state.tts.speak(test_text, blocking=False)
        else:
            st.error("🔊 Text-to-Speech: Not available")


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


personality_info = st.session_state.ai_client.get_current_personality_info()
if personality_info and personality_info.get('name'):
    st.title("💬 {}".format(personality_info.get('name')))
else:
    st.title("💬 Bliss")

if st.session_state.voice_enabled and st.session_state.stt.is_microphone_available():
    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("🎤 Voice Input", help="Click to start voice input"):
            with st.spinner("🎤 Listening..."):
                voice_text = st.session_state.stt.listen_once(timeout=10, phrase_time_limit=15)

            if voice_text:
                st.success(f"You said: {voice_text}")

                st.session_state.messages.append({"role": "user", "content": voice_text})
                with st.chat_message("user"):
                    st.markdown(voice_text)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        try:
                            response = st.session_state.ai_client.generate_response(
                                user_input=voice_text,
                                personality_name=st.session_state.current_personality,
                                session_id=st.session_state.session_id,
                                context_limit=5
                            )
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})

                            if st.session_state.auto_speak_responses and st.session_state.tts.is_available():
                                st.session_state.tts.speak(response, blocking=False)
                        except Exception as e:
                            error_msg = f"Sorry, I encountered an error: {str(e)}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})

                st.rerun()


if not st.session_state.messages:
    greeting = st.session_state.ai_client.get_greeting(st.session_state.current_personality)
    st.session_state.messages.append({"role": "assistant", "content": greeting})

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        col1, col2 = st.columns([10, 1])
        with col1:
            st.markdown(message["content"])
        
        if (message["role"] == "assistant" and st.session_state.voice_enabled and st.session_state.tts.is_available()):
            with col2:
                if st.button("🔊", key=f"speak_{i}", help="Click to hear this message"):
                    st.session_state.tts.speak(message["content"], blocking=False)

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

                if st.session_state.auto_speak_responses and st.session_state.tts.is_available():
                    st.session_state.tts.speak(response, blocking=False)
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.markdown("Bliss is powered by Ollama")