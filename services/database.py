import sqlite3
import json
from datetime import datetime

DB_FILE = "arthdrishti.db"

def init_db():
    """9.1, 9.2, 9.3: Initialize the SQLite database and create tables."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Table for chat conversations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            session_id TEXT PRIMARY KEY,
            messages_json TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Table for fraud checks logging
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            input_data TEXT,
            fraud_score REAL,
            verdict TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_conversation(session_id: str, messages: list):
    """9.4: Inserts or updates the conversation history in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    messages_json = json.dumps(messages)
    
    # Upsert logic: Update if session_id exists, else Insert
    cursor.execute('''
        INSERT INTO conversations (session_id, messages_json, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            messages_json=excluded.messages_json,
            updated_at=excluded.updated_at
    ''', (session_id, messages_json, now, now))
    
    conn.commit()
    conn.close()

def load_conversation(session_id: str) -> list:
    """9.5: Retrieves a conversation from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT messages_json FROM conversations WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return []

def save_fraud_check(session_id: str, data: dict, score: float, verdict: str):
    """9.6: Logs a fraud check to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO fraud_checks (session_id, input_data, fraud_score, verdict, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, json.dumps(data), score, verdict, now))
    
    conn.commit()
    conn.close()
