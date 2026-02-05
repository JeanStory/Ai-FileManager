from app.core.session import Session
from typing import Dict

from logging import getLogger

logger = getLogger(__name__)

class User():
    id: str
    sessions: Dict[str, Session] = {}    # 会话ID到会话对象的映射

    def __init__(self, id: str) -> None:
        self.id = id

    def create_session(self, session_id: str) -> Session:
        if session_id in self.sessions:
            raise ValueError(f"会话 {session_id} 已存在")
        session = Session(id=session_id, user_id=self.id)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            raise ValueError(f"会话 {session_id} 不存在")
        return self.sessions[session_id]
        
users: Dict[str, User] = {}

def get_user(user_id: str) -> User:
    if user_id not in users:
        raise ValueError(f"用户 {user_id} 不存在")
    return users[user_id]
