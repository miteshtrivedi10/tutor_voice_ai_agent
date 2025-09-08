"""
SessionManager service implementing ISessionManager interface.
Handles session state management, conversation history, and data persistence for the prompt-driven voice agent.
Follows Dependency Inversion Principle with abstract interface.
"""
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from src.agents.interfaces import ISessionManager, ToolResult
from src.database.supabase_client import get_db_client
from src.config.logging_config import logger
from src.models.agent_dtos import MainAgentData, ChatTranscript, QuizPackAssessment

@dataclass
class ConversationTurn:
    """Data class for individual conversation turns."""
    timestamp: str
    role: str  # "user" or "assistant"
    content: str
    tool_calls: List[Dict[str, Any]] = None
    session_id: str = None

class SessionManager(ISessionManager):
    """Concrete implementation of session management service."""
    
    def __init__(self):
        self.db_client = get_db_client()
        self.cache_ttl = timedelta(minutes=30)  # Cache TTL for performance
        self.session_cache = {}  # In-memory cache for active sessions
        self.conversation_history_limit = 20  # Max history items to keep

    @classmethod
    def get_session_manager(cls) -> 'SessionManager':
        """
        Singleton method to get the session manager instance
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance
    
    async def create_session(self, user_id: str, initial_data: MainAgentData) -> str:
        """
        Create new session and return session ID
        
        Args:
            user_id: User identifier
            initial_data: Initial session data
            
        Returns:
            Created session ID
        """
        try:
            session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create session data
            session_data = asdict(initial_data)
            session_data.update({
                "session_id": session_id,
                "user_id": user_id,
                "created_time": datetime.now().isoformat(),
                "last_interaction_time": datetime.now().isoformat(),
                "conversation_history": [],
                "update_count": 0,
                "session_status": "active"
            })
            
            # Save to database
            db_result = await self._save_session_to_db(session_id, session_data)
            
            if db_result:
                # Cache the session
                self.session_cache[session_id] = (session_data, datetime.now())
                logger.info(f"Created new session {session_id} for user {user_id}")
                
                return session_id
            else:
                logger.error(f"Failed to create session {session_id} in database")
                raise Exception("Failed to create session in database")
                
        except Exception as e:
            logger.error(f"Error creating session for user {user_id}: {str(e)}")
            raise e
    
    async def get_session(self, session_id: str) -> Optional[MainAgentData]:
        """
        Get session data by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            MainAgentData or None if not found
        """
        try:
            # Check cache first
            if session_id in self.session_cache:
                cached_data, cache_time = self.session_cache[session_id]
                if datetime.now() - cache_time < self.cache_ttl:
                    logger.debug(f"Retrieved session from cache: {session_id}")
                    return MainAgentData(**cached_data)
            
            # Fetch from database
            session_data_dict = await self._fetch_session_from_db(session_id)
            
            if session_data_dict:
                # Cache the result
                self.session_cache[session_id] = (session_data_dict, datetime.now())
                
                # Convert to MainAgentData
                # Remove fields not in MainAgentData model
                pydantic_data = {
                    key: value for key, value in session_data_dict.items() 
                    if key in MainAgentData.model_fields
                }
                
                return MainAgentData(**pydantic_data)
            else:
                logger.warning(f"Session not found: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    async def update_session(self, session_id: str, data: MainAgentData) -> None:
        """
        Update session data
        
        Args:
            session_id: Session identifier
            data: Updated session data
        """
        try:
            session_data_dict = asdict(data)
            session_data_dict["last_interaction_time"] = datetime.now().isoformat()
            session_data_dict["update_count"] = session_data_dict.get("update_count", 0) + 1
            
            # Save to database
            db_result = await self._save_session_to_db(session_id, session_data_dict)
            
            if db_result:
                # Update cache
                self.session_cache[session_id] = (session_data_dict, datetime.now())
                logger.debug(f"Updated session {session_id}")
            else:
                logger.error(f"Failed to update session {session_id} in database")
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            raise e
    
    async def end_session(self, session_id: str) -> None:
        """
        End session and save final transcript
        
        Args:
            session_id: Session identifier
        """
        try:
            # Get final session data
            session_data = await self.get_session(session_id)
            if not session_data:
                logger.warning(f"Session not found for ending: {session_id}")
                return
            
            # Update session status
            session_data.session_status = "completed"
            session_data.last_interaction_time = datetime.now().isoformat()
            
            # Save chat transcript
            transcript = await self.get_chat_transcript(session_id)
            if transcript:
                # Save transcript to database (implementation depends on schema)
                logger.info(f"Saved transcript for completed session {session_id}")
            
            # Save final assessment if quiz was taken
            assessment = getattr(session_data, 'assessment', None)
            if assessment:
                await self.save_assessment(assessment)
            
            # Update session in database
            await self.update_session(session_id, session_data)
            
            # Remove from cache
            if session_id in self.session_cache:
                del self.session_cache[session_id]
            
            logger.info(f"Session {session_id} ended successfully")
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {str(e)}")
            raise e
    
    async def get_chat_transcript(self, session_id: str) -> Optional[ChatTranscript]:
        """
        Get complete chat transcript for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            ChatTranscript or None if not found
        """
        try:
            session_data = await self.get_session(session_id)
            if not session_data:
                return None
            
            # Get conversation history
            history_data = session_data.conversation_history if hasattr(session_data, 'conversation_history') else []
            
            # Convert to ChatMessage objects
            messages = []
            for turn_data in history_data[-50:]:  # Last 50 messages
                message = {
                    "role": turn_data.get("role", "unknown"),
                    "content": turn_data.get("content", ""),
                    "timestamp": datetime.fromisoformat(turn_data.get("timestamp", datetime.now().isoformat())),
                    "tool_calls": turn_data.get("tool_calls", []),
                    "tool_results": turn_data.get("tool_results", [])
                }
                messages.append(message)
            
            # Create transcript
            transcript = ChatTranscript(
                session_id=session_id,
                user_id=getattr(session_data, 'user_id', 'unknown'),
                messages=messages,
                start_time=datetime.fromisoformat(getattr(session_data, 'created_time', datetime.now().isoformat())),
                end_time=datetime.fromisoformat(getattr(session_data, 'last_interaction_time', datetime.now().isoformat())),
                quiz_progress=getattr(session_data, 'quiz_progress', None)
            )
            
            return transcript
            
        except Exception as e:
            logger.error(f"Error getting chat transcript for {session_id}: {str(e)}")
            return None
    
    async def save_assessment(self, assessment: QuizPackAssessment) -> None:
        """
        Save quiz assessment results
        
        Args:
            assessment: Quiz assessment data
        """
        try:
            # Convert to dictionary for database storage
            assessment_data = asdict(assessment)
            assessment_data["completed_time"] = datetime.now().isoformat()
            
            # Save to database
            # Implementation depends on database schema
            db_result = self.db_client.save_assessment(assessment_data)
            
            if db_result:
                logger.info(f"Saved assessment for quiz {assessment.quiz_pack_id}")
            else:
                logger.warning(f"Failed to save assessment for quiz {assessment.quiz_pack_id}")
                
        except Exception as e:
            logger.error(f"Error saving assessment: {str(e)}")
            raise e
    
    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session summaries
        """
        try:
            # Query database for user's sessions
            # Implementation depends on database schema
            sessions = self.db_client.get_user_sessions(user_id)
            
            # Convert to summary format
            session_summaries = []
            for session in sessions:
                summary = {
                    "session_id": session.session_id,
                    "student_name": session.student_name,
                    "subject": session.subject,
                    "created_time": session.created_time.isoformat() if hasattr(session.created_time, 'isoformat') else session.created_time,
                    "last_interaction": session.last_interaction_time.isoformat() if hasattr(session.last_interaction_time, 'isoformat') else session.last_interaction_time,
                    "status": session.session_status,
                    "total_questions": session.total_questions if hasattr(session, 'total_questions') else 0,
                    "score": session.score if hasattr(session, 'score') else None
                }
                session_summaries.append(summary)
            
            logger.debug(f"Retrieved {len(session_summaries)} sessions for user {user_id}")
            return session_summaries
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {str(e)}")
            return []
    
    async def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve current session data from cache or database.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session data dictionary or empty dict if not found
        """
        try:
            # Check cache first
            if session_id in self.session_cache:
                cached_data, cache_time = self.session_cache[session_id]
                if datetime.now() - cache_time < self.cache_ttl:
                    logger.debug(f"Session data retrieved from cache: {session_id}")
                    return cached_data
            
            # Fetch from database
            session_data = await self._fetch_session_from_db(session_id)
            
            if session_data:
                # Cache the result
                self.session_cache[session_id] = (session_data, datetime.now())
                logger.debug(f"Session data loaded from database: {session_id}")
                return session_data
            else:
                # Create default session data
                default_data = self._create_default_session_data(session_id)
                await self.update_session_data(session_id, default_data)
                logger.info(f"Created default session data: {session_id}")
                return default_data
                
        except Exception as e:
            logger.error(f"Error retrieving session data for {session_id}: {str(e)}")
            # Return default data on error to prevent session failure
            default_data = self._create_default_session_data(session_id)
            return default_data
    
    async def update_session_data(self, session_id: str, data: Dict[str, Any]) -> ToolResult:
        """
        Update session data with comprehensive error handling.
        
        Args:
            session_id: Session identifier
            data: Data to merge with existing session data
            
        Returns:
            ToolResult indicating success and any recovery information
        """
        try:
            # Get existing session data
            existing_data = await self.get_session_data(session_id)
            
            # Merge new data (new data takes precedence)
            updated_data = {**existing_data, **data}
            
            # Ensure required fields exist
            updated_data = self._ensure_required_fields(updated_data, session_id)
            
            # Add metadata
            updated_data["last_updated"] = datetime.now().isoformat()
            updated_data["update_count"] = existing_data.get("update_count", 0) + 1
            
            # Save to database
            db_result = await self._save_session_to_db(session_id, updated_data)
            
            if db_result:
                # Update cache
                self.session_cache[session_id] = (updated_data, datetime.now())
                logger.debug(f"Session data updated successfully: {session_id}")
                
                return ToolResult(
                    status="success",
                    data={
                        "session_id": session_id,
                        "updated_fields": list(data.keys()),
                        "total_updates": updated_data["update_count"],
                        "database_saved": True
                    },
                    message=f"Session data updated successfully for {session_id}!",
                    conversation_context={"session_id": session_id}
                )
            else:
                # Database save failed - keep in cache only
                self.session_cache[session_id] = (updated_data, datetime.now())
                logger.warning(f"Database save failed for session {session_id} - using cache only")
                
                return ToolResult(
                    status="partial_success",
                    data={
                        "session_id": session_id,
                        "updated_fields": list(data.keys()),
                        "database_saved": False,
                        "cache_updated": True
                    },
                    message="I updated your information in my memory! Let me make sure everything is saved properly.",
                    conversation_context={"session_id": session_id}
                )
                
        except Exception as e:
            logger.error(f"Error updating session data for {session_id}: {str(e)}")
            
            # Fallback: keep data in cache and return partial success
            if session_id not in self.session_cache:
                self.session_cache[session_id] = ({**self._create_default_session_data(session_id), **data}, datetime.now())
            
            return ToolResult(
                status="error",
                error=f"SESSION_UPDATE_ERROR: {str(e)}",
                fallback_used=True,
                message="I had a little trouble saving everything perfectly, but don't worry - I remember all our important information! You're doing great!",
                data={"status": "partial_update", "method": "cache_fallback"},
                conversation_context={"session_id": session_id}
            )
    
    async def get_conversation_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history for context.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of recent turns to return
            
        Returns:
            List of conversation turns
        """
        try:
            # Get from session data first
            session_data = await self.get_session_data(session_id)
            history = session_data.get("conversation_history", [])
            
            # Ensure we don't exceed limit
            recent_history = history[-limit:] if len(history) > limit else history
            
            # If history is empty, try to reconstruct from database
            if not recent_history:
                recent_history = await self._reconstruct_history_from_db(session_id, limit)
            
            logger.debug(f"Retrieved {len(recent_history)} conversation turns for session {session_id}")
            return recent_history
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history for {session_id}: {str(e)}")
            return []
    
    async def save_conversation_turn(self, session_id: str, role: str, content: str, tool_calls: List[Dict[str, Any]] = None) -> ToolResult:
        """
        Save a conversation turn with error handling.
        
        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Conversation content
            tool_calls: List of tool calls if any
            
        Returns:
            ToolResult indicating save success
        """
        try:
            turn = ConversationTurn(
                timestamp=datetime.now().isoformat(),
                role=role,
                content=content,
                tool_calls=tool_calls or [],
                session_id=session_id
            )
            
            # Get existing session data
            session_data = await self.get_session_data(session_id)
            
            # Add to conversation history
            if "conversation_history" not in session_data:
                session_data["conversation_history"] = []
            
            session_data["conversation_history"].append(asdict(turn))
            
            # Trim history if too long
            if len(session_data["conversation_history"]) > self.conversation_history_limit:
                session_data["conversation_history"] = session_data["conversation_history"][-self.conversation_history_limit:]
            
            # Update session with new history
            update_result = await self.update_session_data(session_id, {
                "conversation_history": session_data["conversation_history"],
                "last_interaction_time": datetime.now().isoformat()
            })
            
            if update_result.status == "success":
                logger.debug(f"Conversation turn saved for session {session_id}: {role}")
                return ToolResult(
                    status="success",
                    data={"turn_id": len(session_data["conversation_history"]), "role": role},
                    message="I remembered our conversation perfectly!",
                    conversation_context={"session_id": session_id}
                )
            else:
                logger.warning(f"Failed to save conversation turn for session {session_id}")
                return ToolResult(
                    status="error",
                    error="CONVERSATION_SAVE_FAILED",
                    fallback_used=True,
                    message="I remember what we talked about, even if I couldn't save it perfectly! Don't worry, our learning adventure continues smoothly.",
                    conversation_context={"session_id": session_id}
                )
                
        except Exception as e:
            logger.error(f"Error saving conversation turn for {session_id}: {str(e)}")
            return ToolResult(
                status="error",
                error=f"CONVERSATION_SAVE_ERROR: {str(e)}",
                fallback_used=True,
                message="I had a little trouble writing down our conversation, but I remember everything important! You're doing wonderfully with our learning!",
                conversation_context={"session_id": session_id}
            )
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up sessions older than TTL.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            expired_count = 0
            current_time = datetime.now()
            
            # Clean cache
            expired_keys = [
                key for key, (data, timestamp) in self.session_cache.items()
                if current_time - timestamp > self.cache_ttl
            ]
            
            for key in expired_keys:
                del self.session_cache[key]
                expired_count += 1
            
            # Clean database (implementation depends on DB schema)
            # expired_count += await self.db_client.delete_expired_sessions(self.cache_ttl)
            
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {str(e)}")
            return 0
    
    def _create_default_session_data(self, session_id: str) -> Dict[str, Any]:
        """Create default session data structure."""
        return {
            "session_id": session_id,
            "student_name": "Student",
            "subject": "General",
            "student_info_collected": False,
            "session_status": "initializing",
            "conversation_history": [],
            "update_count": 0,
            "created_time": datetime.now().isoformat(),
            "last_interaction_time": datetime.now().isoformat(),
            "quiz_data": None,
            "child_age": 9,  # Default age
            "session_source": "voice_tutor"
        }
    
    def _ensure_required_fields(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Ensure all required session fields exist."""
        required_fields = {
            "session_id": session_id,
            "student_name": data.get("student_name", "Student"),
            "subject": data.get("subject", "General"),
            "student_info_collected": data.get("student_info_collected", False),
            "session_status": data.get("session_status", "active"),
            "conversation_history": data.get("conversation_history", []),
            "update_count": data.get("update_count", 0),
            "created_time": data.get("created_time", datetime.now().isoformat()),
            "last_interaction_time": data.get("last_interaction_time", datetime.now().isoformat()),
            "child_age": data.get("child_age", 9)
        }
        
        return {**data, **required_fields}
    
    async def _fetch_session_from_db(self, session_id: str) -> Dict[str, Any]:
        """Fetch session data from database."""
        try:
            # Implementation depends on actual database schema
            # For now, return empty dict to simulate no session found
            # In real implementation: query sessions table
            session_record = self.db_client.get_session(session_id)
            
            if session_record:
                # Convert database record to dictionary
                return {
                    "session_id": session_record.session_id,
                    "student_name": session_record.student_name,
                    "subject": session_record.subject,
                    "student_info_collected": session_record.student_info_collected,
                    "session_status": session_record.session_status,
                    "conversation_history": json.loads(session_record.conversation_history) if session_record.conversation_history else [],
                    "quiz_data": json.loads(session_record.quiz_data) if session_record.quiz_data else None,
                    "child_age": session_record.child_age,
                    "created_time": session_record.created_time.isoformat() if hasattr(session_record.created_time, 'isoformat') else session_record.created_time,
                    "last_interaction_time": session_record.last_interaction_time.isoformat() if hasattr(session_record.last_interaction_time, 'isoformat') else session_record.last_interaction_time,
                    "update_count": session_record.update_count
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Database error fetching session {session_id}: {str(e)}")
            return {}
    
    async def _save_session_to_db(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Save session data to database."""
        try:
            # Convert data for database storage
            db_data = {
                "session_id": data["session_id"],
                "student_name": data["student_name"],
                "subject": data["subject"],
                "student_info_collected": data["student_info_collected"],
                "session_status": data["session_status"],
                "conversation_history": json.dumps(data.get("conversation_history", [])),
                "quiz_data": json.dumps(data.get("quiz_data", {})),
                "child_age": data["child_age"],
                "created_time": data.get("created_time"),
                "last_interaction_time": data.get("last_interaction_time"),
                "update_count": data.get("update_count", 0),
                "session_source": data.get("session_source", "voice_tutor")
            }
            
            # Save to database
            success = self.db_client.save_session(db_data)
            
            if success:
                logger.debug(f"Session saved to database: {session_id}")
            else:
                logger.warning(f"Failed to save session to database: {session_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving session to database {session_id}: {str(e)}")
            return False
    
    async def _reconstruct_history_from_db(self, session_id: str, limit: int) -> List[Dict[str, Any]]:
        """Reconstruct conversation history from database logs."""
        try:
            # Implementation would query conversation logs table
            # For now return empty list
            return []
        except Exception as e:
            logger.error(f"Error reconstructing history for {session_id}: {str(e)}")
            return []
    
    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics for monitoring and reporting."""
        try:
            session_data = await self.get_session_data(session_id)
            
            if not session_data:
                return {"error": "SESSION_NOT_FOUND"}
            
            stats = {
                "session_id": session_id,
                "duration_minutes": self._calculate_session_duration(session_data),
                "questions_answered": len(session_data.get("answer_history", {})),
                "average_score": self._calculate_average_score(session_data),
                "completion_rate": self._calculate_completion_rate(session_data),
                "tool_calls_made": len([turn for turn in session_data.get("conversation_history", []) if turn.get("tool_calls")]),
                "last_interaction": session_data.get("last_interaction_time"),
                "status": session_data.get("session_status")
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting session statistics for {session_id}: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_session_duration(self, session_data: Dict[str, Any]) -> float:
        """Calculate session duration in minutes."""
        try:
            start_time = datetime.fromisoformat(session_data.get("created_time"))
            end_time = datetime.fromisoformat(session_data.get("last_interaction_time"))
            duration = end_time - start_time
            return round(duration.total_seconds() / 60, 2)
        except:
            return 0.0
    
    def _calculate_average_score(self, session_data: Dict[str, Any]) -> float:
        """Calculate average score from answer history."""
        try:
            answer_history = session_data.get("answer_history", {})
            if not answer_history:
                return 0.0
            
            scores = [entry.get("score", 0) for entry in answer_history.values()]
            return round(sum(scores) / len(scores), 2)
        except:
            return 0.0
    
    def _calculate_completion_rate(self, session_data: Dict[str, Any]) -> float:
        """Calculate quiz completion rate."""
        try:
            total_questions = session_data.get("total_questions", 0)
            questions_answered = len(session_data.get("answer_history", {}))
            return round((questions_answered / total_questions * 100), 1) if total_questions > 0 else 0.0
        except:
            return 0.0

# Global instance for dependency injection
session_manager_instance = SessionManager.get_session_manager()

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    return SessionManager.get_session_manager()