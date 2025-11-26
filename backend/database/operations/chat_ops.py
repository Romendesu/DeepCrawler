from database.config import SessionLocal
from database.models.chat_models import Chat, Message
from datetime import datetime

def create_chat(title: str):
    db = SessionLocal()
    chat = Chat(title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def add_message(chat_id: int, sender: str, text: str):
    db = SessionLocal()
    msg = Message(chat_id=chat_id, sender=sender, text=text)
    
    # actualizar el chat
    chat = db.query(Chat).filter_by(id=chat_id).first()
    chat.last_updated = datetime.utcnow()
    
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

