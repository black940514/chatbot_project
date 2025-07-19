from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..config import MAX_CONVERSATION_HISTORY


class Message:
    """Message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        """
        Initialize a message.
        
        Args:
            role: Role of the message sender (user or assistant).
            content: Content of the message.
            timestamp: Timestamp of the message.
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            Dictionary representation of the message.
        """
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary representation of the message.
            
        Returns:
            Message instance.
        """
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class Conversation:
    """Conversation consisting of messages."""
    
    def __init__(self, session_id: str, max_history: int = MAX_CONVERSATION_HISTORY):
        """
        Initialize a conversation.
        
        Args:
            session_id: ID of the conversation session.
            max_history: Maximum number of messages to keep in history.
        """
        self.session_id = session_id
        self.max_history = max_history
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation.
        
        Args:
            role: Role of the message sender (user or assistant).
            content: Content of the message.
        """
        self.messages.append(Message(role, content))
        
        # Trim history if needed
        if len(self.messages) > self.max_history * 2:  # Keep pairs of messages
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history.
        
        Returns:
            List of messages in the conversation.
        """
        return [message.to_dict() for message in self.messages]
    
    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """
        Get the conversation history in a format suitable for LLM.
        
        Returns:
            List of messages in the conversation in LLM format.
        """
        return [{"role": message.role, "content": message.content} for message in self.messages]
    
    def clear(self) -> None:
        """Clear the conversation history."""
        self.messages = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation to a dictionary.
        
        Returns:
            Dictionary representation of the conversation.
        """
        return {
            "session_id": self.session_id,
            "messages": [message.to_dict() for message in self.messages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """
        Create a conversation from a dictionary.
        
        Args:
            data: Dictionary representation of the conversation.
            
        Returns:
            Conversation instance.
        """
        conversation = cls(session_id=data["session_id"])
        conversation.messages = [Message.from_dict(message_data) for message_data in data["messages"]]
        return conversation


class ConversationManager:
    """Manager for multiple conversations."""
    
    def __init__(self):
        """Initialize the conversation manager."""
        self.conversations: Dict[str, Conversation] = {}
    
    def get_conversation(self, session_id: str) -> Conversation:
        """
        Get a conversation by session ID.
        
        Args:
            session_id: ID of the conversation session.
            
        Returns:
            Conversation instance.
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation(session_id)
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        Add a message to a conversation.
        
        Args:
            session_id: ID of the conversation session.
            role: Role of the message sender (user or assistant).
            content: Content of the message.
        """
        conversation = self.get_conversation(session_id)
        conversation.add_message(role, content)
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of a conversation.
        
        Args:
            session_id: ID of the conversation session.
            
        Returns:
            List of messages in the conversation.
        """
        conversation = self.get_conversation(session_id)
        return conversation.get_history()
    
    def get_context_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get the conversation history in a format suitable for LLM.
        
        Args:
            session_id: ID of the conversation session.
            
        Returns:
            List of messages in the conversation in LLM format.
        """
        conversation = self.get_conversation(session_id)
        return conversation.get_context_for_llm()
    
    def clear_conversation(self, session_id: str) -> None:
        """
        Clear a conversation.
        
        Args:
            session_id: ID of the conversation session.
        """
        if session_id in self.conversations:
            self.conversations[session_id].clear()
    
    def delete_conversation(self, session_id: str) -> None:
        """
        Delete a conversation.
        
        Args:
            session_id: ID of the conversation session.
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save all conversations to a file.
        
        Args:
            file_path: Path to the file.
        """
        data = {
            session_id: conversation.to_dict()
            for session_id, conversation in self.conversations.items()
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, file_path: str) -> None:
        """
        Load conversations from a file.
        
        Args:
            file_path: Path to the file.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.conversations = {
            session_id: Conversation.from_dict(conversation_data)
            for session_id, conversation_data in data.items()
        } 