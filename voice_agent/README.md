# Qwen Voice Tutor

A voice-based tutoring agent using LiveKit and AI technologies.

## Setup

1. Install dependencies using `uv`:
```bash
uv sync
```

Or install individually:
```bash
uv add <package_name>
```

2. Configure environment variables in `.env`:
- `SARVAM_API_KEY` - Sarvam API key for STT/TTS
- `GROQ_API_KEY` - Groq API key for LLM
- `LIVEKIT_URL` - LiveKit server URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret

## Running the Application

The application consists of three components:

1. **API Server** - Handles HTTP requests for creating voice sessions and searching the knowledge base:
```bash
python api.py
```

2. **Agent Worker** - Runs the voice agents that connect to LiveKit:
```bash
python main.py
```

## API Endpoints

### Voice Session Endpoints
- `POST /voice/connect` - Create a new voice session
- `POST /voice/disconnect/{room_name}` - Disconnect a voice session

### Search Endpoints
- `POST /search` - Search the knowledge base
- `POST /search/enhanced` - Enhanced search with response synthesis
- `GET /health` - Health check endpoint

## How It Works

1. Frontend calls `/voice/connect` to create a new session
2. API returns room credentials for the client to connect to LiveKit
3. Agent worker automatically starts a voice agent when a user joins the room
4. Frontend can call `/voice/disconnect/{room_name}` to clean up