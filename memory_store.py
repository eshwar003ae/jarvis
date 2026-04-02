import json
import os
from datetime import datetime
from typing import List, Dict, Union
import logging

# 1. SETUP LOGGING
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. YOUR ADVANCED CLASS LOGIC
class ConversationMemory:
    """Handles persistent conversation memory for users"""
    def __init__(self, user_id: str, storage_path: str = "conversations"):
        self.user_id = user_id
        self.storage_path = storage_path
        self.memory_file = os.path.join(storage_path, f"{user_id}_memory.json")
        os.makedirs(storage_path, exist_ok=True)
    
    def load_memory(self) -> List[Dict]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_conversation(self, conversation: Dict) -> bool:
        try:
            memory = self.load_memory()
            if 'timestamp' not in conversation:
                conversation['timestamp'] = datetime.now().isoformat()
            memory.append(conversation)
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get_recent_context(self, max_messages: int = 30) -> List[Dict]:
        memory = self.load_memory()
        all_messages = []
        for conv in memory:
            if "messages" in conv:
                all_messages.extend(conv["messages"])
        return all_messages[-max_messages:]

# 3. THE "BRIDGE" FUNCTIONS (REQUIRED BY BRAIN.PY)
# These functions connect the 'brain' to your Class above.

# This creates one single 'Jarvis' memory instance
_jarvis_mem = ConversationMemory(user_id="Jarvis_System")

def load_memory():
    """brain.py calls this to see past chats"""
    return _jarvis_mem.load_memory()

def save_memory(memory_data):
    """brain.py calls this to save the whole list"""
    return _jarvis_mem.save_conversation({"messages": memory_data})

def get_recent_conversations(limit=30):
    """brain.py calls this to remember what you just said"""
    return _jarvis_mem.get_recent_context(max_messages=limit)

def add_memory_entry(role, content):
    """brain.py calls this to add one new line to the chat"""
    new_msg = {"role": role, "content": content}
    # We load the current list, add the new message, and save it
    return _jarvis_mem.save_conversation({"messages": [new_msg]})
