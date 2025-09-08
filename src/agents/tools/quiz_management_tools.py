"""
Quiz management tools for starting quizzes and getting questions.
Each tool has single responsibility with comprehensive error handling and child-friendly recovery.
"""

from typing import Dict, Any, List
from datetime import datetime
from src.agents.tool_base import BaseTool, ToolResult, FallbackStrategy, RecoveryMessageConfig
from src.database.supabase_client import get_db_client
from src.services.session_manager import get_session_manager
from src.models.agent_dtos import QuizPackFromDb, QnAFromDb  # Existing models


class StartQuizTool(BaseTool):
    """Tool for initializing a new quiz session with question fetching."""
    
    def __init__(self):
        super().__init__(
            name="start_quiz",
            description="Starts a new quiz session by fetching appropriate questions for the selected subject and initializing quiz state. Use this after collecting student information.",
            max_retries=3
        )
        self.db_client = get_db_client()
        self.session_manager = get_session_manager()
        self.emergency_questions = {
            "Science": [
                QnAFromDb(question_id="emergency_1", question="What color is the sky on a sunny day?", answer="Blue"),
                QnAFromDb(question_id="emergency_2", question="What do plants need to grow?", answer="Sunlight and water"),
                QnAFromDb(question_id="emergency_3", question="How many legs does a spider have?", answer="8"),
                QnAFromDb(question_id="emergency_4", question="What is the closest star to Earth?", answer="The Sun"),
                QnAFromDb(question_id="emergency_5", question="What do we call a baby frog?", answer="Tadpole")
            ],
            "English": [
                QnAFromDb(question_id="emergency_1", question="What is the opposite of 'happy'?", answer="Sad"),
                QnAFromDb(question_id="emergency_2", question="How many vowels are in the English alphabet?", answer="5"),
                QnAFromDb(question_id="emergency_3", question="What do we call a baby dog?", answer="Puppy"),
                QnAFromDb(question_id="emergency_4", question="Which word means the same as 'big'?", answer="Large"),
                QnAFromDb(question_id="emergency_5", question="What is the past tense of 'run'?", answer="Ran")
            ],
            "Geography": [
                QnAFromDb(question_id="emergency_1", question="What is the largest ocean in the world?", answer="Pacific Ocean"),
                QnAFromDb(question_id="emergency_2", question="Which continent is the biggest?", answer="Asia"),
                QnAFromDb(question_id="emergency_3", question="What is the capital of India?", answer="New Delhi"),
                QnAFromDb(question_id="emergency_4", question="Which river is the longest in the world?", answer="Nile River"),
                QnAFromDb(question_id="emergency_5", question="What is the biggest desert in the world?", answer="Sahara Desert")
            ]
        }
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Current session ID"},
                "student_name": {"type": "string", "description": "Student's name", "minLength": 1},
                "subject": {"type": "string", "description": "Quiz subject", "enum": ["Science", "English", "Geography"]},
                "number_of_questions": {"type": "number", "description": "Number of questions (default: 5)", "default": 5, "minimum": 1, "maximum": 10},
                "child_age": {"type": "number", "description": "Child's age for question difficulty adjustment", "default": 9}
            },
            "required": ["session_id", "student_name", "subject"]
        }
    
    async def _execute_core(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """Fetch questions and initialize quiz session."""
        try:
            session_id = parameters["session_id"]
            student_name = parameters["student_name"]
            subject = parameters["subject"]
            num_questions = parameters.get("number_of_questions", 5)
            child_age = parameters.get("child_age", 9)
            
            # Validate subject
            if subject not in ["Science", "English", "Geography"]:
                return ToolResult(
                    success=False,
                    error="INVALID_SUBJECT",
                    fallback_action=FallbackStrategy.SIMPLIFIED.value,
                    recovery_message=f"I think {subject} is a great topic, but let me suggest Science, English, or Geography for our questions today! Which would you like?",
                    conversation_context=context
                )
            
            # Fetch questions from database (user_id hardcoded for now - should come from auth)
            user_id = "mitst"  # TODO: Get from session context or authentication
            quiz_pack_result = self.db_client.fetch_random_questions(user_id, subject, num_questions)
            
            if not quiz_pack_result or not quiz_pack_result.quiz_pack:
                # Database fetch failed, try emergency questions
                emergency_result = await self._handle_quiz_pack_failure(session_id, student_name, subject, num_questions, context, child_age)
                if emergency_result.success:
                    return emergency_result
                else:
                    # Even emergency failed - this shouldn't happen
                    return ToolResult(
                        success=False,
                        error="ALL_QUIZ_SOURCES_FAILED",
                        fallback_action=FallbackStrategy.GRACEFUL_END.value,
                        recovery_message="Oh dear! All our question friends seem to be on vacation today! How about we do something else fun like a learning story or guessing game instead?",
                        conversation_context=context
                    )
            
            # Initialize quiz session data
            quiz_data = {
                "student_name": student_name,
                "subject": subject,
                "quiz_pack": [q.__dict__ for q in quiz_pack_result.quiz_pack],
                "current_question_index": 0,
                "score": 0,
                "total_questions": len(quiz_pack_result.quiz_pack),
                "quiz_start_time": datetime.now().isoformat(),
                "child_age": child_age,
                "session_status": "quiz_active",
                "source": "database"
            }
            
            # Save to session
            session_update = await self.session_manager.update_session_data(session_id, quiz_data)
            if not session_update.success:
                # Log warning but consider quiz started with local data
                recovery_msg = f"I got all the questions ready, but let me make sure I saved everything correctly! Anyway, I've got {num_questions} super fun {subject} questions for you, {student_name}! Ready to start our learning adventure?"
            else:
                recovery_msg = f"Amazing! I've got {num_questions} super fun {subject} questions ready for you, {student_name}! They cover all sorts of exciting topics. Ready to start our learning adventure?"
            
            return ToolResult(
                success=True,
                data={
                    "status": "quiz_started",
                    "subject": subject,
                    "total_questions": num_questions,
                    "session_updated": session_update.success,
                    "next_action": "get_next_question",
                    "quiz_data": quiz_data
                },
                recovery_message=recovery_msg,
                conversation_context=context
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"QUIZ_INITIALIZATION_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.EMERGENCY.value,
                recovery_message="Our learning adventure setup is having a little hiccup! Don't worry, I'm fixing it right now. You know what? I think we'll have even more fun with our backup plan!",
                conversation_context=context
            )
    
    async def _handle_quiz_pack_failure(self, session_id: str, student_name: str, subject: str, num_questions: int, context: Dict[str, Any], child_age: int) -> ToolResult:
        """Handle failure to fetch quiz pack from database using emergency questions."""
        # Use emergency questions
        emergency_pack = self.emergency_questions.get(subject, self.emergency_questions["Science"])[:num_questions]
        
        if not emergency_pack:
            return ToolResult(
                success=False,
                error="NO_EMERGENCY_QUESTIONS_AVAILABLE",
                fallback_action=FallbackStrategy.SKIP.value,
                recovery_message=f"All our question friends seem to be out exploring today! How about we play a different learning game or tell a story about {subject} instead?",
                conversation_context=context
            )
        
        quiz_data = {
            "student_name": student_name,
            "subject": subject,
            "quiz_pack": [q.__dict__ for q in emergency_pack],
            "current_question_index": 0,
            "score": 0,
            "total_questions": len(emergency_pack),
            "quiz_start_time": datetime.now().isoformat(),
            "child_age": child_age,
            "session_status": "quiz_active",
            "source": "emergency_questions"  # Flag for monitoring
        }
        
        # Try to save to session
        session_update = await self.session_manager.update_session_data(session_id, quiz_data)
        
        return ToolResult(
            success=True,  # Consider success since we have fallback questions
            data={
                "status": "quiz_started_emergency",
                "subject": subject,
                "total_questions": len(emergency_pack),
                "session_updated": session_update.success,
                "source": "emergency_questions",
                "next_action": "get_next_question",
                "quiz_data": quiz_data
            },
            recovery_message=f"No worries at all! I found some really special {subject} treasure questions just for you, {student_name}! They're some of my very favorites. Ready to begin our special adventure?",
            conversation_context=context
        )
    
    def get_fallback_strategies(self) -> List[str]:
        return [
            FallbackStrategy.RETRY.value,
            FallbackStrategy.CACHED.value,  # Use previous session questions
            FallbackStrategy.EMERGENCY.value,  # Use hardcoded questions
            FallbackStrategy.SKIP.value,  # Skip quiz and do general conversation
            FallbackStrategy.GRACEFUL_END.value
        ]
    
    def _get_recovery_configs(self) -> Dict[str, RecoveryMessageConfig]:
        return {
            **super()._get_recovery_configs(),
            "INVALID_SUBJECT": RecoveryMessageConfig(
                error_type="INVALID_SUBJECT",
                primary_message="That sounds like such an interesting topic! We have our special question collections for Science, English, and Geography. Would you like to try one of those, or did I misunderstand what you wanted to learn about?",
                fallback_message="Every subject is wonderful to learn about! How about we start with Science today? It has questions about animals, space, and nature! Or would you prefer English stories or Geography adventures around the world?",
                tone="encouraging_suggestion",
                age_group="6-12",
                emotional_impact="low"
            ),
            "DATABASE_FETCH_FAILED": RecoveryMessageConfig(
                error_type="DATABASE_FETCH_FAILED",
                primary_message="Our big question library is taking a moment to wake up! While we wait, tell me - what's your favorite thing about {subject}? I bet it's something really cool!",
                fallback_message="No problem at all! Sometimes even the biggest libraries need a little nap. I have some special treasure questions saved just for you that we're going to love!",
                tone="magical_adventure",
                age_group="6-12",
                emotional_impact="medium"
            ),
            "NO_EMERGENCY_QUESTIONS_AVAILABLE": RecoveryMessageConfig(
                error_type="NO_EMERGENCY_QUESTIONS_AVAILABLE",
                primary_message="All our question friends seem to be out exploring today! How about we play a different learning game or tell an exciting story about {subject} instead? What sounds most fun to you?",
                fallback_message="Every learning adventure can take different paths! Would you like to hear a fun story, play a guessing game, or maybe practice with some questions you already know the answers to?",
                tone="flexible_adventure",
                age_group="6-12",
                emotional_impact="low"
            ),
            "ALL_QUIZ_SOURCES_FAILED": RecoveryMessageConfig(
                error_type="ALL_QUIZ_SOURCES_FAILED",
                primary_message="Oh dear! All our question friends seem to be on a big adventure today! How about we do something else really fun like a learning story, guessing game, or explore what you already know about {subject}?",
                fallback_message="Sometimes even the best learning tools need a day off! You're still an amazing learner, and we can always try again tomorrow. What would you like to do in the meantime?",
                tone="graceful_alternative",
                age_group="6-12",
                emotional_impact="medium"
            )
        }


class GetNextQuestionTool(BaseTool):
    """Tool for retrieving and presenting the next quiz question."""
    
    def __init__(self):
        super().__init__(
            name="get_next_question",
            description="Retrieves the next question from the current quiz session and presents it to the student. Tracks progress and handles question flow.",
            max_retries=2
        )
        self.session_manager = get_session_manager()
        self.emergency_question_pool = {
            "Science": [
                "What color is the sky on a sunny day?",
                "What do plants need to grow?",
                "How many legs does a spider have?",
                "What is the closest star to Earth?",
                "What do we call a baby frog?"
            ],
            "English": [
                "What is the opposite of 'happy'?",
                "How many vowels are in the English alphabet?",
                "What do we call a baby dog?",
                "Which word means the same as 'big'?",
                "What is the past tense of 'run'?"
            ],
            "Geography": [
                "What is the largest ocean in the world?",
                "Which continent is the biggest?",
                "What is the capital of India?",
                "Which river is the longest in the world?",
                "What is the biggest desert in the world?"
            ]
        }
    
    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Current session ID"},
                "question_number": {"type": "number", "description": "Specific question number (optional)", "default": None},
                "use_voice_modulation": {"type": "boolean", "description": "Add voice emphasis for engagement", "default": True},
                "child_age": {"type": "number", "description": "Child's age for question complexity", "default": 9}
            },
            "required": ["session_id"]
        }
    
    async def _execute_core(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """Get the next question from the current quiz session."""
        try:
            session_id = parameters["session_id"]
            question_number = parameters.get("question_number")
            child_age = parameters.get("child_age", 9)
            
            # Get current session data
            session_data = await self.session_manager.get_session_data(session_id)
            
            if not session_data or session_data.get("session_status") != "quiz_active":
                subject = session_data.get("subject", "Science") if session_data else "Science"
                return ToolResult(
                    success=False,
                    error="NO_ACTIVE_QUIZ_SESSION",
                    fallback_action=FallbackStrategy.SIMPLIFIED.value,
                    recovery_message=f"I think we need to start our quiz adventure first! Would you like to begin with some fun {subject} questions? We can learn about space, animals, or stories!",
                    conversation_context=context
                )
            
            quiz_pack = session_data.get("quiz_pack", [])
            current_index = session_data.get("current_question_index", 0)
            total_questions = session_data.get("total_questions", len(quiz_pack))
            subject = session_data.get("subject", "Science")
            
            if current_index >= total_questions:
                return ToolResult(
                    success=False,
                    error="QUIZ_COMPLETED",
                    fallback_action=FallbackStrategy.GRACEFUL_END.value,
                    recovery_message="Wow! You've answered all the questions! You did such an amazing job learning and thinking today! Would you like to hear your final score and how wonderfully you did?",
                    conversation_context=context
                )
            
            # Get specific question if requested, otherwise next in sequence
            if question_number is not None and 0 <= question_number < total_questions:
                question_index = question_number
                # Don't advance index for specific question request
                advance_index = False
            else:
                question_index = current_index
                advance_index = True
            
            if question_index >= len(quiz_pack):
                # Use emergency question if we've run out
                emergency_question = await self._get_emergency_question(subject, context)
                if emergency_question:
                    presentation_data = {
                        "question_number": current_index + 1,
                        "total_questions": total_questions,
                        "question_text": emergency_question["question"],
                        "question_id": f"emergency_{current_index}",
                        "subject": subject,
                        "source": "emergency",
                        "hint_available": False,
                        "session_updated": True
                    }
                    recovery_msg = f"Here's a special bonus question for you! Question {current_index + 1}: {emergency_question['question']} What do you think?"
                else:
                    return ToolResult(
                        success=False,
                        error="NO_QUESTIONS_AVAILABLE",
                        fallback_action=FallbackStrategy.SKIP.value,
                        recovery_message="All our questions had a big adventure today! How about we review what we've learned so far or try a different kind of learning game?",
                        conversation_context=context
                    )
            else:
                question_data = quiz_pack[question_index]
                presentation_data = {
                    "question_number": question_index + 1,
                    "total_questions": total_questions,
                    "question_text": question_data.get("question", "What is the capital of France?"),
                    "question_id": question_data.get("question_id", f"q_{question_index}"),
                    "subject": subject,
                    "hint_available": bool(question_data.get("hint", "")),
                    "session_updated": True,
                    "source": "database"
                }
                recovery_msg = f"Here's question {question_index + 1} of {total_questions}! Ready? {presentation_data['question_text']}"
            
            # Update session progress if advancing
            if advance_index:
                session_update = await self.session_manager.update_session_data(
                    session_id,
                    {"current_question_index": current_index + 1}
                )
                presentation_data["session_updated"] = session_update.success
            
            return ToolResult(
                success=True,
                data=presentation_data,
                recovery_message=recovery_msg,
                conversation_context=context
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"QUESTION_RETRIEVAL_ERROR: {str(e)}",
                fallback_action=FallbackStrategy.CACHED.value,
                recovery_message="Oops! That question got shy and hid for a moment. Let me find another really interesting one for you! Here we go - this one's going to be fun!",
                conversation_context=context
            )
    
    async def _get_emergency_question(self, subject: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Get an emergency question when regular questions are unavailable."""
        emergency_pool = self.emergency_question_pool.get(subject, self.emergency_question_pool["Science"])
        
        # Simple round-robin or random selection - for now, just return first available
        if emergency_pool:
            question = emergency_pool[0]  # In real implementation: track used emergency questions
            # Simple answer mapping for emergency questions
            emergency_answers = {
                "Science": ["Blue", "Sunlight and water", "8", "The Sun", "Tadpole"],
                "English": ["Sad", "5", "Puppy", "Large", "Ran"],
                "Geography": ["Pacific Ocean", "Asia", "New Delhi", "Nile River", "Sahara Desert"]
            }
            answer = emergency_answers.get(subject, ["Great answer!"])[0]
            return {"question": question, "answer": answer}
        return None
    
    def get_fallback_strategies(self) -> List[str]:
        return [
            FallbackStrategy.RETRY.value,
            FallbackStrategy.CACHED.value,
            FallbackStrategy.EMERGENCY.value,
            FallbackStrategy.SKIP.value,
            FallbackStrategy.GRACEFUL_END.value
        ]

    def _get_recovery_configs(self) -> Dict[str, RecoveryMessageConfig]:
        return {
            **super()._get_recovery_configs(),
            "NO_ACTIVE_QUIZ_SESSION": RecoveryMessageConfig(
                error_type="NO_ACTIVE_QUIZ_SESSION",
                primary_message="It looks like we haven't started our quiz adventure yet! Would you like to begin with some fun questions about {subject}? We can learn about space, animals, or stories!",
                fallback_message="No worries! Every great learning journey starts with the first step. Shall we choose a subject and get started with our first question?",
                tone="enthusiastic_start",
                age_group="6-12",
                emotional_impact="low"
            ),
            "QUIZ_COMPLETED": RecoveryMessageConfig(
                error_type="QUIZ_COMPLETED",
                primary_message="Congratulations! You've completed all the questions! You did such an amazing job learning and thinking today! Would you like to hear your final score and how wonderfully you did?",
                fallback_message="What an incredible learning adventure we've had! I'm so proud of all your hard work and thinking. Would you like to celebrate with a special story or review what we learned?",
                tone="celebratory_completion",
                age_group="6-12",
                emotional_impact="high_positive"
            ),
            "NO_QUESTIONS_AVAILABLE": RecoveryMessageConfig(
                error_type="NO_QUESTIONS_AVAILABLE",
                primary_message="All our questions had a big adventure today and seem to be exploring! How about we review what we've learned so far or try a different kind of learning game?",
                fallback_message="Sometimes questions like to hide and surprise us! You're still doing wonderfully, and we can always discover new things together in different ways.",
                tone="adventurous_alternative",
                age_group="6-12",
                emotional_impact="low"
            )
        }