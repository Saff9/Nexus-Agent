#!/usr/bin/env python3
"""Session management with SQLite persistence and FTS5 search."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

class Session:
    """Represents a single conversation session."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = self.created_at
        self.messages: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
    
    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to the session."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get message history, optionally limited."""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Deserialize session from dictionary."""
        session = cls(data["id"])
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.updated_at = datetime.fromisoformat(data["updated_at"])
        session.messages = data.get("messages", [])
        session.metadata = data.get("metadata", {})
        return session


class SessionStore:
    """SQLite-based session storage with FTS5 full-text search."""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    updated_at TEXT,
                    data TEXT
                );
                
                CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                    content,
                    content='sessions',
                    content_rowid='rowid'
                );
                
                CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
                    INSERT INTO sessions_fts(rowid, content) 
                    VALUES (NEW.rowid, NEW.data);
                END;
                
                CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at);
            """)
    
    def get_or_create(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create new one."""
        if session_id:
            session = self.get(session_id)
            if session:
                return session
        return Session()
    
    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT data FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return Session.from_dict(json.loads(row["data"]))
        return None
    
    def save(self, session: Session) -> bool:
        """Save session to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sessions (id, created_at, updated_at, data)
                    VALUES (?, ?, ?, ?)
                """, (session.id, session.created_at.isoformat(), 
                      session.updated_at.isoformat(), json.dumps(session.to_dict())))
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def delete(self, session_id: str) -> bool:
        """Delete session by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return True
    
    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, created_at, updated_at 
                FROM sessions 
                ORDER BY updated_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Full-text search across all sessions."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT s.id, s.created_at, s.updated_at, s.data
                FROM sessions s
                JOIN sessions_fts fts ON s.rowid = fts.rowid
                WHERE sessions_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))
            
            results = []
            for row in cursor.fetchall():
                session = Session.from_dict(json.loads(row["data"]))
                results.append({
                    "id": session.id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "snippet": self._find_snippet(session.messages, query)
                })
            return results
    
    def _find_snippet(self, messages: List[Dict], query: str, context: int = 50) -> str:
        """Find relevant snippet from messages matching query."""
        query_lower = query.lower()
        for msg in reversed(messages):
            content = msg.get("content", "")
            if query_lower in content.lower():
                idx = content.lower().find(query_lower)
                start = max(0, idx - context)
                end = min(len(content), idx + len(query) + context)
                return "..." + content[start:end] + "..."
        return ""
