import pyttsx3
import streamlit as st
from typing import Optional, List
import threading
import tempfile
import os

class TextToSpeech:
    def __init__(self):
        self.engine = None
        self._initialize_engine()

    def _initialize_engine(self):
        """
        initialize the TTS engine with error handling
        """
        try:
            self.engine = pyttsx3.init()

            self.engine.setProperty('rate', 180)  # Set speech rate
            self.engine.setProperty('volume', 1.0)  # Set volume level (0.0 to 1.0)

            voices = self.engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break

            st.success("Text-to-Speech engine initialized successfully.")
        except Exception as e:
            st.error(f"Failed to initialize Text-to-Speech engine: {e}")
            self.engine = None

    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.engine or not text.strip():
            st.error("Text-to-Speech engine is not initialized or text is empty.")
            return False
        
        try:
            if blocking:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                thread = threading.Thread(target=self._speak_async, args=(text,))
                thread.daemon = True
                thread.start()
            
            return True
        except Exception as e:
            st.error(f"Speech synthesis error: {e}")
            return False
        
    def _speak_async(self, text: str):
        """
        Asynchronous speech synthesis.
        
        Args:
            text: Text to speak
        """
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            st.error(f"Error during asynchronous speech synthesis: {e}")

    def set_rate(self, rate: int):
        """
        Set the speech rate.
        
        Args:
            rate: Speech rate in words per minute
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
            st.success(f"Speech rate set to {rate} wpm.")
        else:
            st.error("Text-to-Speech engine is not initialized.")

    def set_volume(self, volume: float):
        """
        Set the volume level.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            st.success(f"Volume set to {volume}.")
        else:
            st.error("Text-to-Speech engine is not initialized.")

    def get_voices(self) -> List[dict]:
        """
        Get available voices.
        
        Returns:
            List of dictionaries with voice properties
        """
        if not self.engine:
            return []
        
        voices = []
        try:
            for voice in self.engine.getProperty('voices'):
                voices.append({
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'Languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                })
        
        except Exception:
            pass
        
        return voices
    
    def set_voice(self, voice_id: str):
        """Set the voice by ID."""
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
            except Exception as e:
                st.warning(f"Could not set voice: {e}")
    
    def is_available(self) -> bool:
        """
        Check if TTS is available.
        
        Returns:
            bool: True if TTS engine is initialized, False otherwise
        """
        return self.engine is not None
    
    def save_to_file(self, text: str, filename: str) -> bool:
        """
        Save text to an audio file.
        
        Args:
            text: Text to convert to speech
            filename: Path to save the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.engine or not text.strip():
            st.error("Text-to-Speech engine is not initialized or text is empty.")
            return False
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                self.engine.save_to_file(text, temp_file.name)
                self.engine.runAndWait()
                os.rename(temp_file.name, filename)
            
            st.success(f"Audio saved to {filename}.")
            return True
        except Exception as e:
            st.error(f"Failed to save audio file: {e}")
            return False
        
def create_text_to_speech() -> TextToSpeech:
    """
    Create and return a TextToSpeech instance.
    
    Returns:
        TextToSpeech: Instance of TextToSpeech
    """
    return TextToSpeech()

if __name__ == "__main__":
    tts = create_text_to_speech()
    
    if tts.is_available():
        print("TTS available. Testing...")
        
        voices = tts.get_voices()
        print(f"Available voices: {len(voices)}")
        for voice in voices[:3]:  # Show first 3 voices
            print(f"  - {voice['name']} ({voice['id']})")
        
        test_text = "Hello! This is a test of the text to speech system."
        print(f"Speaking: {test_text}")
        tts.speak(test_text)
    else:
        print("TTS not available")