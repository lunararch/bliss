import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional

class ConversationMemory:
    def __init__(self, db_path: str = 'data/memory.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                create table if not exists conversations (
                    id integer primary key autoincrement,
                    user_input text not null,
                    assistant_response text not null,
                    timestamp datetime default current_timestamp,
                    session_id text default 'default'
                )
            '''
            )

            cursor.execute('''
                create index if not exists idx_timestamp on conversations (timestamp)
            ''')

            conn.commit()
    
    def save_conversation(self, user_input: str, assistant_response: str, session_id: str = 'default'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                insert into conversations (user_input, assistant_response, session_id)
                values (?, ?, ?)
            ''', (user_input, assistant_response, session_id))
            conn.commit()

    def get_recent_conversations(self, limit: int = 10, session_id: str = 'default') -> List[Tuple[str, str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                select user_input, assistant_response, timestamp
                from conversations
                where session_id = ?
                order by timestamp desc
                limit ?
            ''', (session_id, limit))

            return list(reversed(cursor.fetchall()))

    def get_conversation_context(self, limit: int = 5, session_id: str = 'default') -> str:
        conversations = self.get_recent_conversations(limit, session_id)

        context = ""

        for user_input, assistant_response, timestamp in conversations:
            context += f"User: {user_input}\nAssistant: {assistant_response}\nTimestamp: {timestamp}\n\n"

        return context.strip()
    
    def clear_session(self, session_id: str = 'default'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                delete from conversations
                where session_id = ?
            ''', (session_id,))
            conn.commit()

    def get_conversation_count(self, session_id: str = 'default') -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                select count(*)
                from conversations
                where session_id = ?
                ''', (session_id,))
            return cursor.fetchone()[0]