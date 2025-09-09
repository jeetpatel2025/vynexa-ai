import asyncio
import sqlite3
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
import chromadb


class MemoryManager:
    """
    Advanced memory management system for long-term context and learning.
    Features semantic search, conversation summarization, and user preferences.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config.get('db_path', 'data/memory.db')
        self.vector_db_path = config.get('vector_db_path', 'data/chroma_db')
        self.max_context_length = config.get('max_context_length', 10000)
        
        # Initialize databases
        self._init_sqlite_db()
        self._init_vector_db()
    
    def _init_sqlite_db(self):
        """Initialize SQLite database for structured memory storage."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                user_message TEXT,
                assistant_response TEXT,
                timestamp DATETIME,
                session_id TEXT,
                metadata TEXT
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY,
                key TEXT UNIQUE,
                value TEXT,
                updated_at DATETIME
            )
        ''')
        self.conn.commit()
    
    def _init_vector_db(self):
        """Initialize ChromaDB for semantic memory search."""
        self.chroma_client = chromadb.PersistentClient(path=self.vector_db_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="conversation_memory",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def store_interaction(
        self, 
        user_message: str, 
        assistant_response: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Store a conversation interaction in both structured and vector databases.
        
        Args:
            user_message: User's input
            assistant_response: Assistant's response
            session_id: Optional session identifier
            metadata: Additional metadata about the interaction
        """
        timestamp = datetime.now()
        metadata_json = json.dumps(metadata or {})
        
        # Store in SQLite
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO conversations 
            (user_message, assistant_response, timestamp, session_id, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_message, assistant_response, timestamp, session_id, metadata_json))
        
        interaction_id = cursor.lastrowid
        self.conn.commit()
        
        # Store in vector database for semantic search
        combined_text = f"User: {user_message}\nAssistant: {assistant_response}"
        self.collection.add(
            documents=[combined_text],
            metadatas=[{
                'id': interaction_id,
                'timestamp': timestamp.isoformat(),
                'session_id': session_id or 'default'
            }],
            ids=[f"interaction_{interaction_id}"]
        )
    
    async def retrieve_memories(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on semantic similarity.
        
        Args:
            query: Query text to find similar conversations
            limit: Maximum number of memories to retrieve
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant conversation memories
        """
        try:
            # Search vector database
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            memories = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= similarity_threshold:
                        metadata = results['metadatas'][0][i]
                        memories.append({
                            'content': doc,
                            'similarity': similarity,
                            'timestamp': metadata.get('timestamp'),
                            'id': metadata.get('id')
                        })
            
            return memories
            
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    async def summarize_conversation_history(self, session_id: str) -> str:
        """
        Create a summary of past conversations for context.
        
        Args:
            session_id: Session to summarize
            
        Returns:
            Text summary of the conversation history
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_message, assistant_response, timestamp
            FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        ''', (session_id,))
        
        conversations = cursor.fetchall()
        
        if not conversations:
            return "No conversation history available."
        
        # Build summary
        summary_parts = ["Recent conversation summary:"]
        for user_msg, assistant_msg, timestamp in conversations[:5]:  # Last 5 interactions
            summary_parts.append(f"- User asked about: {user_msg[:100]}...")
            summary_parts.append(f"  Assistant helped with: {assistant_msg[:100]}...")
        
        return "\n".join(summary_parts)
    
    async def store_user_preference(self, key: str, value: str):
        """Store a user preference."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now()))
        self.conn.commit()
    
    async def get_user_preference(self, key: str) -> Optional[str]:
        """Retrieve a user preference."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT value FROM user_preferences WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    async def get_conversation_context(
        self, 
        session_id: str, 
        max_tokens: int = 2000
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation context within token limit.
        
        Args:
            session_id: Session identifier
            max_tokens: Maximum tokens to include
            
        Returns:
            List of recent messages formatted for LLM
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT user_message, assistant_response
            FROM conversations 
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))
        
        conversations = cursor.fetchall()
        context = []
        total_length = 0
        
        for user_msg, assistant_msg in conversations:
            msg_length = len(user_msg) + len(assistant_msg)
            if total_length + msg_length > max_tokens:
                break
                
            context.extend([
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_msg}
            ])
            total_length += msg_length
        
        return list(reversed(context))  # Return in chronological order
    
    def cleanup_old_memories(self, days_to_keep: int = 30):
        """Remove old conversation data to manage storage."""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days_to_keep)
        
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE timestamp < ?', (cutoff_date,))
        self.conn.commit()
        
        print(f"Cleaned up conversations older than {days_to_keep} days")
