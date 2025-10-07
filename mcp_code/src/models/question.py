"""
Data models for the MCP Server
Contains typed classes for data structures used throughout the application
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    """Represents a question with its answer from the database"""
    question_id: str
    question: str
    answer: str
    user_name: Optional[str] = None
    subject: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert Question object to dictionary for JSON serialization"""
        return {
            "question_id": self.question_id,
            "question": self.question,
            "answer": self.answer,
            "user_name": self.user_name,
            "subject": self.subject
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Question':
        """Create Question object from dictionary"""
        return cls(
            question_id=data.get("question_id", ""),
            question=data.get("question", ""),
            answer=data.get("answer", ""),
            user_name=data.get("user_name"),
            subject=data.get("subject")
        )