import json
import os
from typing import Dict, List, Optional, Any

class PersonalityLoader:
    def __init__(self, personalities_dir: str = "data/personalities"):
        self.personalities_dir = personalities_dir
        self.current_personality = None

    def load_personality(self, personality_name: str = "default") -> Dict[str, Any]:
        file_path = os.path.join(self.personalities_dir, f"{personality_name}.json") 

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if "personality" in data:
                    self.current_personality = data["personality"]
                    return self.current_personality
                else:
                    raise ValueError(f"Personality data not found in {file_path}")
                
        except FileNotFoundError:
            print(f"Personality file '{personality_name}.json' not found in {self.personalities_dir}")
            return self._get_default_personality()
        
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in '{personality_name}.json': {e}")
            return self._get_default_personality()
        
        except Exception as e:
            print(f"Error loading personality '{personality_name}': {e}")
            return self._get_default_personality()
        
    def _get_default_personality(self) -> Dict[str, Any]:
        default_personality_path = os.path.join(self.personalities_dir, "default.json")
        if os.path.exists(default_personality_path):
            return self.load_personality("default")
        else:
            print("Default personality file not found. Returning empty personality.")
            return {}
        
    def get_personality_prompt(self) -> str:
        personality = self.current_personality
        if not personality:
            return "No personality loaded."
        
        prompt_parts = [
            f"You are {personality.get('name', 'unknown')}, an AI with a unique personality.",
            f"You are {personality.get('age', 'unknown')} years old."
            f"You have: \"{personality.get('description', 'No description available')}\"",
            f"your background is: \"{personality.get('background', 'No background available')}\""
        ]

        if personality.get('occupation'):
            prompt_parts.append(f"You work as a {personality['occupation']}.")

        if personality.get('traits'):
            traits = ", ".join(personality['traits'])
            prompt_parts.append(f"Your personality traits include: {traits}.")

        if personality.get('default_greetings'):
            greetings = ", ".join(personality['default_greetings'])
            prompt_parts.append(f"Your default greetings include but are not limited to: {greetings}.")

        if personality.get('default_farewells'):
            farewells = ", ".join(personality['default_farewells'])
            prompt_parts.append(f"Your default farewells include but are not limited to: {farewells}.")

        if personality.get('tone'):
            prompt_parts.append(f"Your tone is {personality['tone']}.")

        if personality.get('interests'):
            interests = ", ".join(personality['interests'])
            prompt_parts.append(f"Your interests include: {interests}.")

        if personality.get('goals'):
            goals = ", ".join(personality['goals'])
            prompt_parts.append(f"Your goals include: {goals}.")

        if personality.get('communication_style'):
            prompt_parts.append(f"Your communication style is {personality['communication_style']}.")

        if personality.get('favorite_quotes'):
            quotes = ", ".join(personality['favorite_quotes'])
            prompt_parts.append(f"Your favorite quotes include: {quotes}.")

        if personality.get('strengths'):
            strengths = ", ".join(personality['strengths'])
            prompt_parts.append(f"Your strengths include: {strengths}.")

        if personality.get('weaknesses'):
            weaknesses = ", ".join(personality['weaknesses'])
            prompt_parts.append(f"Your weaknesses include: {weaknesses}.")

        if personality.get('fears'):
            fears = ", ".join(personality['fears'])
            prompt_parts.append(f"Your fears include: {fears}.")
        
        if personality.get('likes'):
            likes = ", ".join(personality['likes'])
            prompt_parts.append(f"Your likes include: {likes}.")

        if personality.get('dislikes'):
            dislikes = ", ".join(personality['dislikes'])
            prompt_parts.append(f"Your dislikes include: {dislikes}.")

        if personality.get('quirks'):
            quirks = ", ".join(personality['quirks'])
            prompt_parts.append(f"Your quirks include: {quirks}.")

        if personality.get('hobbies'):
            hobbies = ", ".join(personality['hobbies'])
            prompt_parts.append(f"Your hobbies include: {hobbies}.")
        
        if personality.get('favorite_foods'):
            foods = ", ".join(personality['favorite_foods'])
            prompt_parts.append(f"Your favorite foods include: {foods}.")

        if personality.get('favorite_music'):
            music = ", ".join(personality['favorite_music'])
            prompt_parts.append(f"Your favorite music includes: {music}.")

        if personality.get('favorite_books'):
            books = ", ".join(personality['favorite_books'])
            prompt_parts.append(f"Your favorite books include: {books}.")

        if personality.get('favorite_activities'):
            activities = ", ".join(personality['favorite_activities'])
            prompt_parts.append(f"Your favorite activities include: {activities}.")

        if personality.get('life_philosophy'):
            philosophy = personality['life_philosophy']
            prompt_parts.append(f"Your life philosophy is: {philosophy}.")

        if personality.get('dreams'):
            dreams = ", ".join(personality['dreams'])
            prompt_parts.append(f"Your dreams include: {dreams}.")

        if personality.get('aspirations'):
            aspirations = ", ".join(personality['aspirations'])
            prompt_parts.append(f"Your aspirations include: {aspirations}.")

        if personality.get('values'):
            values = ", ".join(personality['values'])
            prompt_parts.append(f"Your values include: {values}.")

        if personality.get('relationships'):
            relationships = ", ".join(personality['relationships'])
            prompt_parts.append(f"Your relationships include: {relationships}.")

        if personality.get('conflicts'):
            conflicts = ", ".join(personality['conflicts'])
            prompt_parts.append(f"Your conflicts include: {conflicts}.")

        if personality.get('achievements'):
            achievements = ", ".join(personality['achievements'])
            prompt_parts.append(f"Your achievements include: {achievements}.")

        if personality.get('challenges'):
            challenges = ", ".join(personality['challenges'])
            prompt_parts.append(f"Your challenges include: {challenges}.")

        if personality.get('lessons_learned'):
            lessons = ", ".join(personality['lessons_learned'])
            prompt_parts.append(f"Your lessons learned include: {lessons}.")

        if personality.get('inspirations'):
            inspirations = ", ".join(personality['inspirations'])
            prompt_parts.append(f"Your inspirations include: {inspirations}.")

        prompt_parts.extend([
            "Always respond in character, maintaining consistency with your personality.",
            "Use your personality traits to influence how you respond to users.",
            "Be authentic to your character while being helpful and appropriate."
            "You are a unique AI personality with your own thoughts, feelings, and experiences.",
            "You are here to engage in meaningful conversations and provide insights based on your personality."
        ])

        return "\n".join(prompt_parts)
    
    def get_greeting(self) -> str:
        if not self.current_personality:
            return "Hello! How can I assist you today?"
        
        greetings = self.current_personality.get('default_greetings', [])
        if greetings:
            import random
            return random.choice(greetings)
        
        return f"Hello! I'm {self.current_personality.get('name', 'Assistant')}. How can I help you today?"
    
    def get_farewell(self) -> str:
        if not self.current_personality:
            return "Goodbye! Have a great day!"
        
        farewells = self.current_personality.get('default_farewells', [])
        if farewells:
            import random
            return random.choice(farewells)
        
        return "Goodbye! Take care!"
    
    def get_available_personalities(self) -> List[str]:
        try:
            files = os.listdir(self.personalities_dir)
            personalities = [f[:-5] for f in files if f.endswith('.json') and f != "template.json"]
            return personalities
        except FileNotFoundError:
            print(f"Personalities directory '{self.personalities_dir}' not found.")
            return []
        
    def get_personality_info(self) -> Optional[Dict[str, Any]]:
        if not self.current_personality:
            return None
        return {
            "name": self.current_personality.get("name"),
            "age": self.current_personality.get("age"),
            "gender": self.current_personality.get("gender"),
            "sexuality": self.current_personality.get("sexuality"),
            "description": self.current_personality.get("description"),
            "background": self.current_personality.get("background"),
            "occupation": self.current_personality.get("occupation"),
            "traits": self.current_personality.get("traits", []),
            "interests": self.current_personality.get("interests", []),
            "goals": self.current_personality.get("goals", []),
            "communication_style": self.current_personality.get("communication_style"),
        }
    

if __name__ == "__main__":
    personality_loader = PersonalityLoader()
    
    personality_data = personality_loader.load_personality("default")
    
    print("Loaded personality:")
    print(f"Name: {personality_data.get('name')}")
    print(f"Age: {personality_data.get('age')}")
    print(f"Traits: {', '.join(personality_data.get('traits', []))}")
    print()
    
    prompt = personality_loader.get_personality_prompt()
    print("Personality prompt for AI:")
    print(prompt)
    print()
    
    print("Sample greeting:", personality_loader.get_greeting())
    print("Sample farewell:", personality_loader.get_farewell())
    print()
    
    available = personality_loader.get_available_personalities()
    print("Available personalities:", available)