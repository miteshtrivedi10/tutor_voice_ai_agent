"""
GetNextQuestionTool - Single responsibility tool for retrieving the next quiz question
Implements progressive learning with adaptive difficulty and comprehensive error handling
"""
from typing import Dict, Any, List
import random
import logging
from datetime import datetime

from src.agents.interfaces import ITool, ToolExecutionContext
from src.models.agent_dtos import MainAgentData, QuizPackAssessment, QnAFromDb


logger = logging.getLogger(__name__)

# Mock quiz data - in production, this would come from database or quiz service
MOCK_QUIZ_DATA = {
    "Science": {
        "easy": [
            QnAFromDb(id="s1", question="What color is the sky on a clear day?", answer="Blue"),
            QnAFromDb(id="s2", question="What do plants need to grow?", answer="Sunlight and water"),
            QnAFromDb(id="s3", question="How many legs does a spider have?", answer="8")
        ],
        "medium": [
            QnAFromDb(id="s4", question="What is the chemical symbol for water?", answer="H2O"),
            QnAFromDb(id="s5", question="What planet is known as the Red Planet?", answer="Mars"),
            QnAFromDb(id="s6", question="What force keeps us on the ground?", answer="Gravity")
        ],
        "hard": [
            QnAFromDb(id="s7", question="What is the powerhouse of the cell?", answer="Mitochondria"),
            QnAFromDb(id="s8", question="What is the speed of light?", answer="300,000 km/s"),
            QnAFromDb(id="s9", question="What element has atomic number 1?", answer="Hydrogen")
        ]
    },
    "English": {
        "easy": [
            QnAFromDb(id="e1", question="What is the opposite of 'happy'?", answer="Sad"),
            QnAFromDb(id="e2", question="How many vowels are in the English alphabet?", answer="5"),
            QnAFromDb(id="e3", question="What is the plural of 'cat'?", answer="Cats")
        ],
        "medium": [
            QnAFromDb(id="e4", question="What is a simile?", answer="Comparison using like or as"),
            QnAFromDb(id="e5", question="What is the past tense of 'go'?", answer="Went"),
            QnAFromDb(id="e6", question="What is an adjective?", answer="Describes a noun")
        ],
        "hard": [
            QnAFromDb(id="e7", question="What is iambic pentameter?", answer="5 pairs of unstressed-stressed syllables"),
            QnAFromDb(id="e8", question="What is the literary device of repetition called?", answer="Anaphora"),
            QnAFromDb(id="e9", question="What is the term for a word that reads the same forwards and backwards?", answer="Palindrome")
        ]
    },
    "Geography": {
        "easy": [
            QnAFromDb(id="g1", question="What is the largest ocean?", answer="Pacific Ocean"),
            QnAFromDb(id="g2", question="What continent is the biggest?", answer="Asia"),
            QnAFromDb(id="g3", question="What is the capital of India?", answer="New Delhi")
        ],
        "medium": [
            QnAFromDb(id="g4", question="What is the longest river in the world?", answer="Nile River"),
            QnAFromDb(id="g5", question="What mountain range separates Europe and Asia?", answer="Ural Mountains"),
            QnAFromDb(id="g6", question="What desert covers much of northern Africa?", answer="Sahara Desert")
        ],
        "hard": [
            QnAFromDb(id="g7", question="What is the smallest country by land area?", answer="Vatican City"),
            QnAFromDb(id="g8", question="What is the deepest point in the ocean?", answer="Mariana Trench"),
            QnAFromDb(id="g9", question="What is the only continent without an active volcano?", answer="Australia")
        ]
    }
}


class GetNextQuestionTool(ITool):
    """Tool for retrieving the next question in a quiz session"""
    
    def __init__(self):
        self.current_questions: List[QnAFromDb] = []
        self.current_index = 0
        self.used_questions: set = set()
    
    @property
    def name(self) -> str:
        return "get_next_question"
    
    @property
    def description(self) -> str:
        return (
            "Get the next question for the current quiz session. Use this after starting a quiz "
            "and after each student answer. The tool tracks progress, selects appropriate questions "
            "based on difficulty and subject, and provides hints if needed. It returns the question "
            "text, multiple choice options (if applicable), and tracks the student's progress."
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "request_hint": {
                    "type": "boolean",
                    "description": "Whether to provide a hint for the current question",
                    "default": False
                },
                "skip_question": {
                    "type": "boolean", 
                    "description": "Whether to skip the current question and get a new one",
                    "default": False
                }
            },
            "required": []
        }
    
    async def execute(self, parameters: Dict[str, Any], context: ToolExecutionContext) -> Dict[str, Any]:
        """
        Execute the tool to get the next quiz question
        
        Args:
            parameters: Dict containing request_hint (optional), skip_question (optional)
            context: Execution context with session data
            
        Returns:
            Dict with the next question and quiz progress information
        """
        try:
            session_data = context.session_data
            assessment = session_data.assessment
            
            # Validate quiz session is active
            if not assessment or not session_data.current_quiz_id:
                raise ValueError("No active quiz session. Please start a quiz first using start_quiz tool.")
            
            # Check if quiz is complete
            if assessment.completed_questions >= assessment.total_questions:
                return {
                    "success": True,
                    "quiz_complete": True,
                    "message": (
                        f"🎉 Congratulations {session_data.student_name}! You've completed your quiz! "
                        f"You answered {assessment.completed_questions} questions. "
                        f"Let's review what you learned and see how you did! "
                        f"Would you like to see your results or try another quiz?"
                    ),
                    "next_action": "end_quiz",
                    "final_score": assessment.score if assessment.score is not None else "Calculating...",
                    "total_questions": assessment.total_questions
                }
            
            # Handle skip request
            if parameters.get("skip_question", False):
                self.current_index += 1
                assessment.completed_questions += 1
                session_data.quiz_progress = assessment.completed_questions
                
                if self.current_index >= len(self.current_questions):
                    # End of questions, complete quiz
                    assessment.end_time = datetime.now()
                    return {
                        "success": True,
                        "quiz_complete": True,
                        "message": (
                            f"📚 We've covered all the questions for today, {session_data.student_name}! "
                            f"You've been learning about {session_data.subject} and I'm proud of your effort! "
                            f"Let's wrap up this session. Would you like to review what we covered?"
                        ),
                        "next_action": "end_quiz",
                        "questions_completed": assessment.total_questions
                    }
                
                # Get next question after skip
                question = self._get_current_question(session_data)
                
                return {
                    "success": True,
                    "skipped": True,
                    "message": (
                        f"✅ Okay, {session_data.student_name}! I've skipped that question for now. "
                        f"Here's your next question about {session_data.subject}. Take your time! "
                        f"Remember, it's okay to skip questions - we can always come back to them later! 😊"
                    ),
                    "question": question,
                    "progress": f"{assessment.completed_questions}/{assessment.total_questions}",
                    "next_action": "wait_for_answer"
                }
            
            # Get or initialize current question
            if not self.current_questions:
                self._initialize_questions(session_data, assessment)
            
            if self.current_index >= len(self.current_questions):
                # Shouldn't happen, but safety check
                assessment.end_time = datetime.now()
                return {
                    "success": True,
                    "quiz_complete": True,
                    "message": (
                        f"🎓 Excellent work {session_data.student_name}! We've completed all the questions "
                        f"for your {session_data.subject} quiz. You should be proud of what you've accomplished! "
                        f"Let's see how you did overall."
                    ),
                    "next_action": "end_quiz",
                    "total_questions": assessment.total_questions
                }
            
            question = self._get_current_question(session_data)
            hint_requested = parameters.get("request_hint", False)
            hint = self._get_hint(question) if hint_requested else None
            
            progress = f"{assessment.completed_questions + 1}/{assessment.total_questions}"
            
            response_message = (
                f"📝 Question {progress}: {question.question} "
                f"{'(Hint: ' + hint + ')' if hint else ''}"
            )
            
            if random.random() < 0.3:  # 30% chance for encouragement
                response_message += f"\n\n💡 {self._get_encouragement(session_data.student_name)}"
            
            logger.info(
                f"Delivered question {self.current_index + 1} to {session_data.student_name}: "
                f"{question.question[:50]}..."
            )
            
            return {
                "success": True,
                "question": question,
                "question_id": question.id,
                "hint": hint,
                "progress": progress,
                "message": response_message,
                "total_questions": assessment.total_questions,
                "next_action": "wait_for_answer",
                "quiz_type": assessment.quiz_pack_id.split('_')[1] if '_' in assessment.quiz_pack_id else "practice"
            }
            
        except ValueError as ve:
            logger.error(f"Quiz session error: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error getting next question: {str(e)}")
            raise e
    
    def _initialize_questions(self, session_data: MainAgentData, assessment: QuizPackAssessment):
        """Initialize questions for the current quiz session"""
        try:
            subject = session_data.subject
            difficulty = assessment.difficulty_level
            
            if subject not in MOCK_QUIZ_DATA:
                raise ValueError(f"Subject '{subject}' not supported")
            
            available_questions = MOCK_QUIZ_DATA[subject][difficulty]
            
            # Select random questions based on total needed
            total_needed = min(assessment.total_questions, len(available_questions))
            self.current_questions = random.sample(list(available_questions), total_needed)
            self.current_index = 0
            self.used_questions.clear()
            
            logger.info(f"Initialized {total_needed} questions for {subject} {difficulty} quiz")
            
        except Exception as e:
            logger.error(f"Error initializing questions: {str(e)}")
            # Fallback to easy questions
            self.current_questions = MOCK_QUIZ_DATA.get("Science", {}).get("easy", [])[:5]
            self.current_index = 0
    
    def _get_current_question(self, session_data: MainAgentData) -> QnAFromDb:
        """Get the current question from the quiz sequence"""
        if not self.current_questions:
            raise ValueError("No questions available in current quiz session")
        
        question = self.current_questions[self.current_index]
        return question
    
    def _get_hint(self, question: QnAFromDb) -> str:
        """Generate a helpful hint for the question"""
        hints = {
            "s1": "Think about what you see when you look up on a sunny day!",
            "s2": "Plants are like little green factories. What do they need to make their food?",
            "s3": "Count the legs on a spider - it's more than a dog but less than a centipede!",
            "s4": "Water is made of hydrogen and oxygen. What's the formula?",
            "s5": "This planet is red and has the tallest mountain in the solar system!",
            "s6": "This invisible force pulls everything toward the center of the Earth.",
            "s7": "This organelle is where cells make energy - remember the phrase!",
            "s8": "Light travels very fast - about 186,000 miles per second!",
            "s9": "The first element in the periodic table is the simplest one.",
            "e1": "Think of a feeling that's the opposite of smiling.",
            "e2": "Remember the song: A, E, I, O, U!",
            "e3": "When you have more than one cat, what do you call them?",
            "e4": "It's a comparison that uses 'like' or 'as' - 'as brave as a lion'!",
            "e5": "Yesterday I ___ to the store.",
            "e6": "It tells you more about a person, place, or thing.",
            "g1": "It's the biggest and touches Asia, Australia, and the Americas!",
            "g2": "Home to China, India, and Russia - the most populous continent!",
            "g3": "India's capital is in the north and has many historical sites.",
            "g4": "This African river is famous for ancient Egyptian civilization.",
            "g5": "This mountain range runs north-south through Russia.",
            "g6": "The largest hot desert in the world, mostly in North Africa.",
        }
        
        return hints.get(question.id, "Think about what you've learned in class!")
    
    def _get_encouragement(self, student_name: str) -> str:
        """Get random encouragement message"""
        encouragements = [
            f"You're doing great, {student_name}! Keep up the good thinking!",
            f"Excellent effort, {student_name}! I can see you're really concentrating!",
            f"Wonderful, {student_name}! Every question helps you learn more!",
            f"You're a learning superstar, {student_name}! 🌟",
            f"Amazing work, {student_name}! You're getting smarter with each answer!"
        ]
        return random.choice(encouragements)
    
    def get_child_friendly_error(self, error: Exception) -> str:
        """
        Get child-friendly error message for question retrieval failures
        
        Args:
            error: The exception that occurred
            
        Returns:
            Child-friendly error message with recovery guidance
        """
        error_msg = str(error).lower()
        
        if "no active quiz" in error_msg:
            return (
                "Oops! I think we need to start a quiz first before I can ask you questions. "
                "Would you like to begin learning {session_data.subject}? "
                "Just say 'yes' and I'll get your first question ready! 📚"
            )
        elif "complete" in error_msg or "all the questions" in error_msg:
            return (
                "🎉 Yay! You've answered all the questions! I'm so proud of you for completing the quiz! "
                "Let's see how you did and maybe try another fun learning activity next time! "
                "What did you think of the questions?"
            )
        elif "question" in error_msg:
            return (
                "Hmm, I had a little trouble getting your next question. Don't worry! "
                "Let's try asking for a new one. Would you like me to give you another question about "
                "{session_data.subject}? I'm sure I can find a really interesting one for you! 🔄"
            )
        else:
            return (
                "Oh no! Something went wrong with getting your question. Technology can be tricky sometimes! 😊 "
                "No worries at all - let's try again. Would you like me to ask you a question about "
                "{session_data.subject}? I promise this one will work perfectly! "
                "Remember, learning is about trying and I'm here to help you every step of the way!"
            )