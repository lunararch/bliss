from core.personality import PersonalityLoader

def setup_personality(personality_name: str = "default") -> PersonalityLoader:
    loader = PersonalityLoader()
    loader.load_personality(personality_name)
    return loader

def get_personality_enhanced_prompt(user_input: str, personality_loader: PersonalityLoader, context: str = "") -> str:
    personality_prompt = personality_loader.get_personality_prompt()
    full_prompt = f"""{personality_prompt}
        {f"previous conversation context: {context}" if context else ""}
        User: {user_input}
        Respond in character as {personality_loader.current_personality.get('name')}
    """

    return full_prompt

if __name__ == "__main__":
    personality = setup_personality("default")
    
    user_message = "Hello, how are you today?"
    ai_prompt = get_personality_enhanced_prompt(user_message, personality)
    
    print("Complete AI prompt:")
    print(ai_prompt)