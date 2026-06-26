import uuid
import os
from services.database import save_conversation, load_conversation

sessions = {}

SEBI_DISCLAIMER = "\nDISCLAIMER: I am an AI financial educator, not a SEBI-registered advisor. Please consult a certified financial planner before making any investment decisions. I cannot provide specific stock or fund recommendations."

# UPGRADED: Now accepts a 'mode' parameter to load different brains
def get_system_prompt(mode: str) -> str:
    if mode == "money_mgmt":
        file_path = "prompts/money_mgmt_prompt.txt"
    elif mode == "fraud":
        file_path = "prompts/fraud_prompt.txt"
    else:
        file_path = "prompts/profiler_prompt.txt"
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            prompt_text = f.read()
            if mode == "profiler":
                return prompt_text.replace("{sebi_disclaimer}", SEBI_DISCLAIMER)
            return prompt_text
    except FileNotFoundError:
        return "You are a helpful financial AI."
# databse
def create_session() -> str:
    return str(uuid.uuid4())

def get_history(session_id: str) -> list:
    if session_id not in sessions:
        # 9.5: Try to load from Database if the server restarted
        db_history = load_conversation(session_id)
        if db_history:
            sessions[session_id] = db_history
        else:
            return []
    return sessions.get(session_id, [])

def add_message(session_id: str, role: str, content: str, mode: str = "profiler"):
    history = get_history(session_id)
    
    if not history:
        history = [
            {"role": "system", "content": get_system_prompt(mode)}
        ]
    
    history.append({"role": role, "content": content})
    
    # Enforce the 30-message limit
    if len(history) > 31:
        history = [history[0]] + history[-30:]
        
    # Save to memory for speed
    sessions[session_id] = history
    
    # 9.4: Save to SQLite for persistence
    save_conversation(session_id, history)