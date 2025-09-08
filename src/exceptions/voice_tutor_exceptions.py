"""
Custom exceptions for the voice tutor application
"""


class VoiceTutorException(Exception):
    """Base exception for the voice tutor application"""
    pass


class ConfigurationException(VoiceTutorException):
    """Exception raised for configuration errors"""
    pass


class DatabaseException(VoiceTutorException):
    """Exception raised for database errors"""
    pass


class QuizException(VoiceTutorException):
    """Exception raised for quiz-related errors"""
    pass


class VoiceProcessingException(VoiceTutorException):
    """Exception raised for voice processing errors"""
    pass


class AgentException(VoiceTutorException):
    """Exception raised for agent-related errors"""
    pass