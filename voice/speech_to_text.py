import speech_recognition as sr
import streamlit as st
from typing import Optional
import threading
import queue
import time


class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """
        Listen for a single phrase and return the recognized text.
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time to record a phrase
            
        Returns:
            str: Recognized text or None if failed
        """
        try:
            with self.microphone as source:
                st.info("Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            st.info("Processing Speech...")
            text = self.recognizer.recognize_tensorflow(audio)
            return text
        except sr.WaitTimeoutError:
            st.error("Listening timed out. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("Could not understand the audio. Please try again.")
            return None
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
            return None
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None
        
    def continuous_listen(self, result_queue: queue.Queue, stop_event: threading.Event):
        """
        Continuously listen for speech and put recognized text into a queue.
        
        Args:
            queue: Queue to store recognized text
            stop_event: Event to signal stopping the listening
        """
        while not stop_event.is_set():
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                
                text = self.recognizer.recognize_tensorflow(audio)
                result_queue.put(('success', text))

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                result_queue.put(('error', "Could not understand the audio."))
            except sr.RequestError as e:
                result_queue.put(('error', f"Could not request results; {e}"))
                break
            except Exception as e:
                result_queue.put(('error', f"An error occurred: {e}"))
                break

    def is_microphone_available(self) -> bool:
        """
        Check if the microphone is available.
        
        Returns:
            bool: True if microphone is available, False otherwise
        """
        try:
            sr.Microphone.list_microphone_names()
            return True
        except Exception as e:
            st.error(f"Microphone not available: {e}")
            return False
        
def create_speech_to_text() -> SpeechToText:
    """
    Factory method to create an instance of SpeechtToText.
    
    Returns:
        SpeechtToText: Instance of the class
    """
    return SpeechToText()
    
if __name__ == "__main__":
    stt = create_speech_to_text()
    
    if stt.is_microphone_available():
        print("Microphone available. Testing speech recognition...")
        print("Say something!")
        
        result = stt.listen_once(timeout=10)
        if result:
            print(f"You said: {result}")
        else:
            print("No speech recognized")
    else:
        print("Microphone not available")
