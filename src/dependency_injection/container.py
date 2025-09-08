"""
Dependency injection container for the voice tutor application
"""
from typing import Any, Dict, Type, TypeVar
from src.config.config_manager import get_config_manager
from src.database.supabase_client import get_db_client
from src.services.usage_service import UsageService
from src.qa_metrics.evaluator import initialise_answer_evaluator


T = TypeVar('T')


class DIContainer:
    """Dependency injection container"""
    
    _instance = None
    _services: Dict[Type, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DIContainer, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        # Register default services
        self._register_default_services()
        self._initialized = True
    
    def _register_default_services(self) -> None:
        """Register default services"""
        self._services[type(get_config_manager())] = get_config_manager()
        self._services[type(get_db_client())] = get_db_client()
        self._services[UsageService] = UsageService()
        self._services[type(initialise_answer_evaluator())] = initialise_answer_evaluator()
    
    def register(self, service_type: Type[T], instance: T) -> None:
        """
        Register a service instance
        
        Args:
            service_type: Type of the service
            instance: Service instance
        """
        self._services[service_type] = instance
    
    def get(self, service_type: Type[T]) -> T:
        """
        Get a service instance
        
        Args:
            service_type: Type of the service
            
        Returns:
            Service instance
        """
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")
        return self._services[service_type]


def get_container() -> DIContainer:
    """Get the singleton DI container instance"""
    return DIContainer()