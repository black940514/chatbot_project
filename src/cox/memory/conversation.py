from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from ..config import MAX_CONVERSATION_HISTORY


class Message:
    """
    대화에서 주고받는 메시지 클래스
    """
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        # role: 'user' 또는 'assistant'
        # content: 메시지 내용
        # timestamp: 메시지를 보낸 시각 (없으면 현재 시간 사용)
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Message 객체를 JSON 딕셔너리로 변경
        """
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        딕셔너리 데이터를 받아 Message 객체로 복원
        """
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )



class Conversation:
    """
    한 세션의 메시지 히스토리를 저장
    """
    def __init__(self, session_id: str, max_history: int = MAX_CONVERSATION_HISTORY):
        # session_id: 대화 세션을 구분하는 고유 ID
        # max_history: 보관할 최대 메시지 쌍 수
        self.session_id = session_id
        self.max_history = max_history
        self.messages: List[Message] = []  # Message 객체 리스트

    def add_message(self, role: str, content: str) -> None:
        """
        새 메시지 추가, 오래된 메시지는 자름
        """
        self.messages.append(Message(role, content))
        # messages가 (질문+답변) 쌍 기준으로 max_history*2를 넘으면 앞쪽을 자름
        
        if len(self.messages) > self.max_history * 2:
            self.messages = self.messages[-self.max_history * 2:]

    def get_history(self) -> List[Dict[str, Any]]:
        """
        전체 메시지를 딕셔너리 리스트로 반환
        """
        return [msg.to_dict() for msg in self.messages]

    def get_context_for_llm(self) -> List[Dict[str, str]]:
        """
        LLM 입력 포맷(role, content)으로 변환
        """
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]

    def clear(self) -> None:
        """
        대화 기록 삭제
        """
        self.messages = []

    def to_dict(self) -> Dict[str, Any]:
        """
        Conversation 전체를 딕셔너리로 변환
        """
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """
        딕셔너리 데이터를 받아 Conversation 객체로 복원
        """
        conv = cls(session_id=data["session_id"])
        conv.messages = [Message.from_dict(m) for m in data["messages"]]
        return conv


class ConversationManager:
    """
    여러 Conversation 인스턴스를 생성·조회·삭제
    """
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}

    def get_conversation(self, session_id: str) -> Conversation:
        """
        session_id에 해당하는 Conversation을 반환
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation(session_id)
        return self.conversations[session_id]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        세션에 메시지를 추가
        """
        conv = self.get_conversation(session_id)
        conv.add_message(role, content)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        세션의 전체 메시지 기록 반환
        """
        return self.get_conversation(session_id).get_history()

    def get_context_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """
        세션메시지를 LLM 포맷 반환
        """
        return self.get_conversation(session_id).get_context_for_llm()

    def clear_conversation(self, session_id: str) -> None:
        """
        특정 세션의 대화 기록 초기화
        """
        if session_id in self.conversations:
            self.conversations[session_id].clear()

    def delete_conversation(self, session_id: str) -> None:
        """
        특정 세션을 삭제
        """
        if session_id in self.conversations:
            del self.conversations[session_id]

    def save_to_file(self, file_path: str) -> None:
        """
        모든 세션을 JSON 파일로 저장
        """
        data = {sid: conv.to_dict() for sid, conv in self.conversations.items()}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, file_path: str) -> None:
        """
        JSON 파일에서 세션 데이터를 읽어와 복원
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.conversations = {
            sid: Conversation.from_dict(conv_data)
            for sid, conv_data in data.items()
        }