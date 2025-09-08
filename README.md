# Voice Agent

A voice-based tutoring agent built with LiveKit and Python.

## Project Structure

```
voice_agent/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── tutor_agent.py
│   ├── run_quiz_agent.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logging_config.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── supabase_client.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── agent_dtos.py
│   ├── qa_metrics/
│   │   ├── __init__.py
│   │   └── pedant.py
│   └── utils/
│       ├── __init__.py
│       └── open_telemtry.py
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