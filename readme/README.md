# Voice Agent

A voice-based tutoring agent built with LiveKit and Python.

## Project Structure

```
voice_agent/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── interfaces.py
│   │   └── tutor_agent.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── config_manager.py
│   │   └── logging_config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   └── supabase_client.py
│   ├── dependency_injection/
│   │   ├── __init__.py
│   │   └── container.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── voice_tutor_exceptions.py
│   ├── factories/
│   │   ├── __init__.py
│   │   └── agent_factory.py
│   ├── logging/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── agent_dtos.py
│   ├── qa_metrics/
│   │   ├── __init__.py
│   │   └── evaluator.py
│   ├── quiz/
│   │   ├── __init__.py
│   │   └── quiz_engine.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── usage_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── open_telemtry.py
│   └── voice/
│       ├── __init__.py
│       └── voice_processing.py
├── tests/
├── migrations/
└── ...
```

## Installation

1. Install the required dependencies:
   ```bash
   pip install -e .
   ```

## Usage

To run the voice agent:
```bash
python -m src.main
```

## Configuration

The application is configured using environment variables defined in a `.env` file. See `src/config/settings.py` for available configuration options.

## Database

The application uses Supabase for data storage. Database migrations are stored in the `migrations/` directory.

## Testing

Run tests with:
```bash
pytest tests/
```

## Architecture

This application follows SOLID principles and has a modular architecture:

- **Agents**: Contains agent implementations and interfaces
- **Config**: Configuration management
- **Database**: Database access layer with repository pattern
- **Dependency Injection**: DI container for service management
- **Exceptions**: Custom exception classes
- **Factories**: Object creation factories
- **Logging**: Custom logging implementation
- **Models**: Data transfer objects
- **QA Metrics**: Question answering evaluation
- **Quiz**: Quiz engine and related functionality
- **Services**: Business logic services
- **Utils**: Utility functions
- **Voice**: Voice processing components