import ollama
import json
from typing import List, Dict, Optional

try:
    from .personality import PersonalityLoader
    from .memory import ConversationMemory
except ImportError:
    from personality import PersonalityLoader
    from memory import ConversationMemory

class OllamaClient:
    def __init__(self, model_name: str = 'mistral'):
        """
        Initialize the Ollama client with the specified model.
        
        Args:
            model_name (str): Name of the Ollama model to use (default: mistral)
        """
        self.model_name = model_name
        self.client = ollama
        self.personality_loader = PersonalityLoader()
        self.memory = ConversationMemory()
    
    def generate_response(self, user_input: str, personality_name: str = "default", 
                         session_id: str = "default", context_limit: int = 5) -> str:
        """
        Generate a response using the Ollama model with personality and conversation context.
        
        Args:
            user_input (str): The user's message
            personality_name (str): Name of personality to load from data/personalities/
            session_id (str): Session identifier for conversation memory
            context_limit (int): Number of recent conversations to include as context
            
        Returns:
            str: Generated response from the model
        """
        try:
            personality_data = self.personality_loader.load_personality(personality_name)
            
            conversation_context = self.memory.get_recent_conversations(context_limit, session_id)
            
            system_prompt = self.personality_loader.get_personality_prompt()
            
            messages = self._build_messages(system_prompt, user_input, conversation_context)
            
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'num_predict': 500
                }
            )
            
            ai_response = response['message']['content'].strip()
            
            self.memory.save_conversation(user_input, ai_response, session_id)
            
            return ai_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            error_response = "I'm sorry, I couldn't process that request."
            self.memory.save_conversation(user_input, error_response, session_id)
            return error_response
    
    def _build_messages(self, system_prompt: str, user_input: str, 
                       conversation_context: List[tuple] = None) -> List[Dict]:
        """
        Build the message array for the Ollama chat API.
        
        Args:
            system_prompt (str): System/personality prompt from PersonalityLoader
            user_input (str): Current user message
            conversation_context (list): Previous conversation turns from ConversationMemory
            
        Returns:
            list: Formatted messages for Ollama API
        """
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if conversation_context:
            for user_msg, assistant_msg, timestamp in conversation_context:
                messages.append({"role": "user", "content": user_msg})
                messages.append({"role": "assistant", "content": assistant_msg})
        
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def get_greeting(self, personality_name: str = "default") -> str:
        """
        Get a greeting from the loaded personality.
        
        Args:
            personality_name (str): Name of personality to use
            
        Returns:
            str: Greeting message
        """
        self.personality_loader.load_personality(personality_name)
        return self.personality_loader.get_greeting()
    
    def get_farewell(self, personality_name: str = "default") -> str:
        """
        Get a farewell from the loaded personality.
        
        Args:
            personality_name (str): Name of personality to use
            
        Returns:
            str: Farewell message
        """
        self.personality_loader.load_personality(personality_name)
        return self.personality_loader.get_farewell()
    
    def get_conversation_count(self, session_id: str = "default") -> int:
        """
        Get the number of conversations in the current session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            int: Number of conversations
        """
        return self.memory.get_conversation_count(session_id)
    
    def clear_conversation_memory(self, session_id: str = "default") -> None:
        """
        Clear conversation memory for a session.
        
        Args:
            session_id (str): Session identifier to clear
        """
        self.memory.clear_session(session_id)
        print(f"Conversation memory cleared for session: {session_id}")
    
    def get_available_personalities(self) -> List[str]:
        """
        Get list of available personalities.
        
        Returns:
            list: Available personality names
        """
        return self.personality_loader.get_available_personalities()
    
    def get_current_personality_info(self) -> Optional[Dict]:
        """
        Get information about the currently loaded personality.
        
        Returns:
            dict: Personality information or None if no personality loaded
        """
        return self.personality_loader.get_personality_info()
    
    def test_connection(self) -> bool:
        """
        Test if Ollama is running and the model is available.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            print("Testing Ollama connection...")

            models_response = self.client.list()
            print(f"Raw response type: {type(models_response)}")
            
            model_names = []
            if hasattr(models_response, 'models'):
                models = models_response.models
                print(f"Found {len(models)} models")
                
                for model in models:
                    if hasattr(model, 'model'):
                        # Extract model name (e.g., 'mistral:latest' -> 'mistral:latest')
                        model_name = model.model
                        model_names.append(model_name)
                        print(f"  - {model_name}")
            else:
                print(f"✗ Unexpected response format: {type(models_response)}")
                return False
            
            print(f"Available models: {model_names}")
            
            model_found = False
            matched_model = None
            
            for name in model_names:
                if name == self.model_name:
                    model_found = True
                    matched_model = name
                    break
                # Check if our model name is in the full name (e.g., 'mistral' in 'mistral:latest')
                elif self.model_name in name:
                    model_found = True
                    matched_model = name
                    self.model_name = name
                    break
            
            if model_found:
                print(f"✓ Connected to Ollama with model: {matched_model}")
                return True
            else:
                print(f"✗ Model '{self.model_name}' not found.")
                print(f"Available models: {model_names}")
                print(f"Try: ollama pull {self.model_name}")
                return False
                
        except Exception as e:
            print(f"✗ Failed to connect to Ollama: {e}")
            print("Make sure Ollama is running with: ollama serve")
            import traceback
            traceback.print_exc()
            return False

def create_ai_client(model_name: str = "mistral") -> OllamaClient:
    """
    Create and return an OllamaClient instance.
    
    Args:
        model_name (str): Name of the Ollama model to use
        
    Returns:
        OllamaClient: Configured client instance
    """
    return OllamaClient(model_name)

if __name__ == "__main__":
    print("Starting AI Client test...")

    client = create_ai_client("mistral")
    
    if client.test_connection():
        print("\n" + "="*50)
        print("OLLAMA CONNECTION SUCCESSFUL!")
        print("="*50)
        
        try:
            print("Available personalities:", client.get_available_personalities())
            print()
            
            greeting = client.get_greeting("default")
            print(f"Greeting: {greeting}")
            print()
            
            test_session = "test_session"
            
            response1 = client.generate_response(
                "Hello! What's your name?",
                personality_name="default",
                session_id=test_session
            )
            print(f"Response 1: {response1}")
            print()
            
            response2 = client.generate_response(
                "What are your hobbies?",
                personality_name="default",
                session_id=test_session
            )
            print(f"Response 2: {response2}")
            print()
            
            print(f"Conversation count: {client.get_conversation_count(test_session)}")
            
            personality_info = client.get_current_personality_info()
            if personality_info:
                print(f"Current personality: {personality_info.get('name', 'Unknown')} - {personality_info.get('description', 'No description')}")
            
            farewell = client.get_farewell("default")
            print(f"Farewell: {farewell}")
            
            client.clear_conversation_memory(test_session)
            print(f"Cleared session. New count: {client.get_conversation_count(test_session)}")
            
        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n" + "="*50)
        print("OLLAMA CONNECTION FAILED!")
        print("="*50)
        print("Please check:")
        print("1. Is Ollama running? Run: ollama serve")
        print("2. Is Mistral installed? Run: ollama pull mistral")
        print("3. Check available models: ollama list")