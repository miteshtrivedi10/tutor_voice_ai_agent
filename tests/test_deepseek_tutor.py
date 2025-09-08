import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from core.deepseek_tutor import TutorVoiceAgent, QuizSession, QuizResult, fetch_qna, evaluation_tool, SessionUserData

class TestQuizSession:
    def test_quiz_session_initialization(self):
        """Test that QuizSession initializes correctly"""
        session = QuizSession()
        assert session.current_question_index == 0
        assert session.quiz_results == []
        assert session.qna_set == []
        assert session.student_name == ""
    
    def test_add_result(self):
        """Test adding a result to the quiz session"""
        session = QuizSession()
        result = QuizResult(
            question="What is 2+2?",
            correct_answer="4",
            student_answer="4",
            is_correct=True
        )
        session.add_result(result)
        assert len(session.quiz_results) == 1
        assert session.quiz_results[0] == result
    
    def test_calculate_score(self):
        """Test calculating quiz score"""
        session = QuizSession()
        # Add some results
        session.add_result(QuizResult("Q1", "A1", "A1", True))
        session.add_result(QuizResult("Q2", "A2", "A2", True))
        session.add_result(QuizResult("Q3", "A3", "A3", False))
        
        score = session.calculate_score()
        assert score == pytest.approx(66.67, 0.01)  # 2 out of 3 correct
    
    def test_calculate_score_empty(self):
        """Test calculating score with no results"""
        session = QuizSession()
        score = session.calculate_score()
        assert score == 0.0

class TestFunctions:
    @pytest.mark.asyncio
    async def test_fetch_qna(self):
        """Test fetching Q&A pairs"""
        result = await fetch_qna("science", 2)
        assert isinstance(result, list)
        assert len(result) == 4  # Fixed set of questions in the mock
        assert "question" in result[0]
        assert "answer" in result[0]
    
    @pytest.mark.asyncio
    async def test_evaluation_tool(self):
        """Test the evaluation tool"""
        # Test with matching answers
        result = await evaluation_tool("What is 2+2?", "4", "4")
        assert result == True
        # Test with non-matching answers
        result = await evaluation_tool("What is 2+2?", "4", "5")
        assert result == False

if __name__ == "__main__":
    pytest.main([__file__])