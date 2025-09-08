"""
Agent factory for creating voice agents in the tutor application
"""
from livekit.agents import JobContext

from src.agents.tutor_agent import TutorVoiceAgent


class AgentFactory:
    """Factory for creating voice agents"""
    
    @staticmethod
    def create_tutor_agent(ctx: JobContext) -> TutorVoiceAgent:
        """
        Create a tutor voice agent
        
        Args:
            ctx (JobContext): The job context
            
        Returns:
            TutorVoiceAgent: The created tutor agent
        """
        return TutorVoiceAgent(ctx=ctx)