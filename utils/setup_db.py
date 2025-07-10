from core.memory import ConversationMemory
import os

def setup_database():
    print("Setting up the database...")

    memory = ConversationMemory()

    if os.path.exists(memory.db_path):
        print("✅ Database created successfully at data/memory.db")
        print(f"✅ Current conversation count: {memory.get_conversation_count()}")
    else:
        print("❌ Failed to create database")
        return False
    
        return True

if __name__ == "__main__":
    setup_database()