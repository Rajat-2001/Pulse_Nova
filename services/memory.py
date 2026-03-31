# services/memory.py

# Store conversation history per session
# Key = session_id, Value = list of messages
conversation_store = {}

MAX_HISTORY = 10  # keep last 10 exchanges

def get_history(session_id: str) -> list:
    """Get conversation history for a session"""
    return conversation_store.get(session_id, [])

def add_message(session_id: str, role: str, content: str):
    """Add a message to conversation history"""
    if session_id not in conversation_store:
        conversation_store[session_id] = []
    
    conversation_store[session_id].append({
        "role": role,
        "content": content
    })
    
    # ✅ Keep only last MAX_HISTORY messages
    if len(conversation_store[session_id]) > MAX_HISTORY * 2:
        conversation_store[session_id] = conversation_store[session_id][-MAX_HISTORY * 2:]

def clear_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_store:
        del conversation_store[session_id]
    return {"status": "cleared"}

def get_all_sessions() -> list:
    """List all active sessions"""
    return list(conversation_store.keys())