"""
EvaluateAnswerTool: Scores student answers using LLM semantic evaluation with fallback mechanisms.
Single responsibility: Answer evaluation with comprehensive error handling and child-friendly feedback.
"""
from typing import Dict, Any, List
import asyncio
from src.agents.tool_base import BaseTool, ToolResult, FallbackStrategy, RecoveryMessageConfig
from src.services.session_manager import SessionManager
from src.services.llm_service import LLMService  # Will be implemented for model integration
from src.database.supabase_client import get_db_client

class EvaluateAnswerTool(BaseTool):
    """Tool for evaluating student answers with semantic analysis and scoring."""
    
    def __init__(self):
        super().__init__(
            name="evaluate_answer",
            description="Evaluates a student's answer to a quiz question using semantic understanding. Provides scoring, feedback, and learning encouragement. Use this after the student responds to a question.",
            max_retries=2
        )
        self.session_manager = SessionManager()
        self.llm_service = LLMService(model="meta-llama/llama-3.1-8b-instruct:free")  # Selected model
        self.db_client = get_db_client()
        self.keyword_threshold = 0.6  # For fallback keyword matching
        self.perfect_score_keywords = ["exactly", "perfect", "spot on", "correct"]
        self.good_score_keywords = ["close", "almost", "good", "right idea"]
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Current session ID"},
                "question_id": {"type": "string", "description": "ID of the question being answered"},
                "student_answer": {"type": "string", "description": "Student's spoken/written answer"},
                "question_text": {"type": "string", "description": "Original question text for context"},
                "correct_answer": {"type": "string", "description": "Correct answer for evaluation", "optional": True},
                "child_age": {"type": "number", "description": "Child's age for feedback tone adjustment", "default": 9},
                "hint_used": {"type": "boolean", "description": "Whether student used a hint", "default": False}
            },
            "required": ["session_id", "question_id", "student_answer", "question_text"]
        }
    
    async def _execute_core(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """Evaluate student answer using semantic analysis with fallbacks."""
        try:
            session_id = parameters["session_id"]
            question_id = parameters["question_id"]
            student_answer = parameters["student_answer"].strip()
            question_text = parameters["question_text"]
            correct_answer = parameters.get("correct_answer")
            child_age = parameters.get("child_age", 9)
            hint_used = parameters.get("hint_used", False)
            
            if not student_answer:
                return ToolResult(
                    success=False,
                    error="EMPTY_STUDENT_ANSWER",
                    fallback_action=FallbackStrategy.SIMPLIFIED.value,
                    recovery_message="I think I missed your answer! Could you tell me what you think one more time? Don't worry, there's no wrong answer when you're learning!",
                    conversation_context=context
                )
            
            # Get session context for scoring
            session_data = await self.session_manager.get_session_data(session_id)
            if not session_data or session_data.get("session_status") != "quiz_active":
                return ToolResult(
                    success=False,
                    error="NO_ACTIVE_QUIZ_CONTEXT",
                    fallback_action=FallbackStrategy.SKIP.value,
                    recovery_message="I need to know which question we're talking about! Let me check our learning adventure... Oh, I think we need to get the next question ready first!",
                    conversation_context=context
                )
            
            # Try semantic evaluation first (LLM-based)
            semantic_result = await self._evaluate_semantic(student_answer, correct_answer or "", question_text, context)
            
            if semantic_result.success:
                # Update session score
                score_update = await self._update_session_score(session_id, semantic_result.data["score"], question_id, student_answer, hint_used)
                
                feedback_data = {
                    **semantic_result.data,
                    "session_updated": score_update.success,
                    "hint_used": hint_used,
                    "question_id": question_id,
                    "student_age_group": "young" if child_age < 8 else "older"
                }
                
                return ToolResult(
                    success=True,
                    data=feedback_data,
                    recovery_message=semantic_result.recovery_message,
                    conversation_context=context
                )
            else:
                # Semantic evaluation failed, try keyword fallback
                return await self._handle_semantic_failure(student_answer, correct_answer or "", question_text, session_id, question_id, context, hint_used, child_age)
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"ANSWER_EVALUATION_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.SIMPLIFIED.value,
                recovery_message="I had a little trouble checking your answer right now, but I can tell you put a lot of thought into it! That's what matters most in learning. Let me give you a special encouragement star and we'll move to the next question!",
                conversation_context=context
            )
    
    async def _evaluate_semantic(self, student_answer: str, correct_answer: str, question_text: str, context: Dict[str, Any]) -> ToolResult:
        """Perform semantic evaluation using LLM."""
        try:
            # Get session subject for context
            session_data = await self.session_manager.get_session_data(context.get("session_id", ""))
            subject = session_data.get("subject", "General") if session_data else "General"
            
            # Create evaluation prompt for LLM
            evaluation_prompt = f"""
You are evaluating a child's answer to an educational quiz question. The child is {context.get('child_age', 9)} years old.

QUIZ CONTEXT:
- Subject: {subject}
- Question: {question_text}
- Correct Answer: {correct_answer}
- Student Answer: {student_answer}

EVALUATION CRITERIA:
1. For children, focus on effort, reasoning, and partial understanding
2. Give credit for close answers or good thought process
3. Be encouraging even for incorrect answers
4. Consider if the child used a hint (adjust expectations accordingly)

Please provide:
1. score: 0-1.0 (floating point, where 1.0 = perfect, 0.5 = partial credit, 0.0 = no credit)
2. correctness_category: "perfect", "good", "partial", "incorrect" 
3. reasoning_explanation: Brief explanation of why this score (for logging)
4. encouragement_message: Child-friendly positive feedback
5. learning_tip: Gentle suggestion for improvement (if needed)

RESPONSE FORMAT (JSON only):
{{
  "score": 0.85,
  "correctness_category": "good", 
  "reasoning_explanation": "Student showed good understanding but missed specific detail",
  "encouragement_message": "That's a really good answer! You understood the main idea perfectly!",
  "learning_tip": "Next time, remember that specific detail about [concept]"
}}

Remember: Always be encouraging and focus on the learning process!
"""
            
            # Call LLM service
            llm_response = await self.llm_service.generate_response(
                prompt=evaluation_prompt,
                model="meta-llama/llama-3.1-8b-instruct:free",
                max_tokens=300,
                temperature=0.3  # Low temperature for consistent evaluation
            )
            
            if not llm_response or "score" not in llm_response:
                return ToolResult(
                    success=False,
                    error="LLM_EVALUATION_FAILED",
                    fallback_action=FallbackStrategy.SIMPLIFIED.value,
                    recovery_message="My thinking helper is taking a moment! But I can tell from your answer that you really thought carefully about the question. That's fantastic learning behavior!",
                    conversation_context=context
                )
            
            # Parse LLM response
            score = float(llm_response.get("score", 0.0))
            category = llm_response.get("correctness_category", "partial")
            encouragement = llm_response.get("encouragement_message", "Great effort!")
            learning_tip = llm_response.get("learning_tip", "")
            
            # Map semantic score to integer for session tracking
            int_score = 1 if score >= 0.7 else 0
            
            return ToolResult(
                success=True,
                data={
                    "semantic_score": score,
                    "int_score": int_score,
                    "category": category,
                    "encouragement": encouragement,
                    "learning_tip": learning_tip,
                    "evaluation_method": "semantic_llm",
                    "llm_confidence": score  # Use score as confidence proxy
                },
                recovery_message=encouragement,
                conversation_context=context
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"SEMANTIC_EVALUATION_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.SIMPLIFIED.value,
                recovery_message="My special answer checker is having a little nap! Don't worry though - I can tell you put lots of thought into your answer, and that's what makes you such a wonderful learner!",
                conversation_context=context
            )
    
    async def _handle_semantic_failure(self, student_answer: str, correct_answer: str, question_text: str, session_id: str, question_id: str, context: Dict[str, Any], hint_used: bool, child_age: int) -> ToolResult:
        """Handle semantic evaluation failure with keyword matching fallback."""
        try:
            # Simple keyword matching fallback
            student_words = set(student_answer.lower().split())
            correct_words = set(correct_answer.lower().split())
            
            # Calculate overlap
            common_words = student_words.intersection(correct_words)
            overlap_ratio = len(common_words) / max(len(student_words), len(correct_words), 1)
            
            # Determine score based on overlap
            if overlap_ratio >= 0.8:
                score = 1
                category = "perfect"
                encouragement = "That's exactly right! You got it perfectly!"
            elif overlap_ratio >= 0.5:
                score = 1
                category = "good"  
                encouragement = "Excellent! You got the main idea perfectly!"
            elif overlap_ratio >= 0.2:
                score = 0
                category = "partial"
                encouragement = "Great thinking! You understood part of it really well!"
            else:
                score = 0
                category = "incorrect"
                encouragement = "That's a very interesting way to think about it! Let me share the correct answer so we can both learn something new!"
            
            # Adjust for hint usage
            if hint_used and score == 1:
                encouragement = "Fantastic! You used the hint so well and got it exactly right!"
            
            # Update session score
            score_update = await self._update_session_score(session_id, score, question_id, student_answer, hint_used)
            
            # Get correct answer explanation if available
            explanation = await self._get_answer_explanation(question_id, correct_answer, context)
            
            feedback_data = {
                "keyword_score": overlap_ratio,
                "int_score": score,
                "category": category,
                "encouragement": encouragement,
                "explanation": explanation,
                "learning_tip": "Keep practicing - each answer helps you get even better!",
                "evaluation_method": "keyword_fallback",
                "hint_used": hint_used,
                "session_updated": score_update.success
            }
            
            return ToolResult(
                success=True,
                data=feedback_data,
                recovery_message=f"{encouragement} {explanation}",
                conversation_context=context
            )
            
        except Exception as e:
            # Final fallback - positive reinforcement without scoring
            return ToolResult(
                success=True,  # Consider success to avoid infinite fallback loop
                data={
                    "int_score": 1,  # Give credit for effort
                    "category": "effort_based",
                    "encouragement": "I love how much thought you put into that answer! That's exactly the kind of learning attitude that makes you such a wonderful student!",
                    "explanation": "Great effort on this question!",
                    "learning_tip": "Your curiosity and willingness to try are more important than any single answer!",
                    "evaluation_method": "positive_reinforcement",
                    "session_updated": False
                },
                recovery_message="I love how much thought you put into that answer! That's exactly the kind of learning attitude that makes you such a wonderful student! Let's give that question a special encouragement star and move to our next adventure!",
                conversation_context=context
            )
    
    async def _update_session_score(self, session_id: str, score: int, question_id: str, student_answer: str, hint_used: bool) -> ToolResult:
        """Update session score and answer history."""
        try:
            session_data = await self.session_manager.get_session_data(session_id)
            
            if session_data and session_data.get("session_status") == "quiz_active":
                # Update score
                current_score = session_data.get("score", 0)
                updated_score = current_score + score
                total_questions = session_data.get("total_questions", 1)
                
                # Update answer history
                answer_history = session_data.get("answer_history", {})
                answer_history[question_id] = {
                    "question_id": question_id,
                    "student_answer": student_answer,
                    "score": score,
                    "hint_used": hint_used,
                    "timestamp": datetime.now().isoformat(),
                    "evaluation_method": "semantic_llm"  # Will be updated in fallback
                }
                
                update_data = {
                    "score": updated_score,
                    "answer_history": answer_history,
                    "questions_answered": len(answer_history),
                    "last_question_time": datetime.now().isoformat()
                }
                
                session_update = await self.session_manager.update_session_data(session_id, update_data)
                return ToolResult(success=session_update.success)
            else:
                return ToolResult(success=False, error="CANNOT_UPDATE_INACTIVE_SESSION")
                
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"SCORE_UPDATE_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.SKIP.value
            )
    
    async def _get_answer_explanation(self, question_id: str, correct_answer: str, context: Dict[str, Any]) -> str:
        """Get explanation for correct answer."""
        try:
            # Try to get explanation from database first
            explanation_data = self.db_client.get_question_explanation(question_id)
            if explanation_data and explanation_data.explanation:
                return explanation_data.explanation
            
            # Generate simple explanation using correct answer
            subject = context.get("subject", "General")
            explanations = {
                "Science": f"The correct answer is '{correct_answer}'. This is important because it helps us understand how {subject.lower()} works in the real world!",
                "English": f"The correct answer is '{correct_answer}'. Understanding words like this helps us communicate better and express our ideas clearly!",
                "Geography": f"The correct answer is '{correct_answer}'. Knowing about places like this helps us understand how big and amazing our world is!"
            }
            
            return explanations.get(subject, f"The correct answer is '{correct_answer}'. Great job learning about this!")
            
        except Exception:
            return f"The correct answer is '{correct_answer}'. This is a very interesting fact that helps us learn more about the world!"
    
    def get_fallback_strategies(self) -> List[str]:
        return [
            FallbackStrategy.RETRY.value,
            FallbackStrategy.SIMPLIFIED.value,  # Keyword matching
            FallbackStrategy.CACHED.value,  # Use previous evaluation patterns
            FallbackStrategy.SKIP.value,  # Skip evaluation, give partial credit
            FallbackStrategy.GRACEFUL_END.value
        ]
    
    def _get_recovery_configs(self) -> Dict[str, RecoveryMessageConfig]:
        return {
            **super()._get_recovery_configs(),
            "EMPTY_STUDENT_ANSWER": RecoveryMessageConfig(
                error_type="EMPTY_STUDENT_ANSWER",
                primary_message="I think I missed your answer! Could you tell me what you think one more time? Don't worry, there's no wrong answer when you're learning - every thought counts!",
                fallback_message="That's okay! Sometimes we need a moment to think. Take your time and share your idea whenever you're ready. I can't wait to hear what you think!",
                tone="patient_encouragement",
                age_group="6-12",
                emotional_impact="low"
            ),
            "LLM_EVALUATION_FAILED": RecoveryMessageConfig(
                error_type="LLM_EVALUATION_FAILED",
                primary_message="My special thinking helper is taking a little break! But I can tell from your answer that you really thought carefully about the question. That's fantastic learning behavior! Let me give you a special encouragement star!",
                fallback_message="Sometimes even the smartest helpers need a moment! The most important thing is that you tried your very best, and that's what makes you such an amazing learner. You get full credit for effort!",
                tone="positive_reinforcement",
                age_group="6-12",
                emotional_impact="low"
            ),
            "SEMANTIC_EVALUATION_ERROR": RecoveryMessageConfig(
                error_type="SEMANTIC_EVALUATION_ERROR",
                primary_message="My answer understanding magic is having a little hiccup! Don't worry though - I can tell you put lots of thought into your answer, and that's what matters most in learning. You get a thinking star for great effort!",
                fallback_message="Even the best magic sometimes needs a recharge! Your willingness to think carefully and try your best is more important than any single answer. You're doing wonderful learning work!",
                tone="magical_encouragement",
                age_group="6-12",
                emotional_impact="low"
            ),
            "NO_ACTIVE_QUIZ_CONTEXT": RecoveryMessageConfig(
                error_type="NO_ACTIVE_QUIZ_CONTEXT",
                primary_message="I need to know which question we're talking about! Let me check our learning adventure... Oh, I think we need to get the next question ready first! Would you like me to find a fun new question for you?",
                fallback_message="Sometimes our learning map gets a little mixed up! No problem at all - let me get everything organized again. Would you like to continue with our next question or start fresh with something new?",
                tone="helpful_reorganization",
                age_group="6-12",
                emotional_impact="low"
            )
        }