# Voice Tutor Agent - Tool-Based Architecture

A comprehensive voice-based educational tutoring agent built with LiveKit, Python, and advanced LLM integration. The application has been refactored from a stepwise task-based system to a modern, SOLID-compliant tool-based architecture.

## 🎯 Features

- **Natural Conversation Flow**: Single agent with comprehensive system prompt driving educational interactions
- **Tool-Based Architecture**: Modular tools for specific operations (student info, quiz management, answer evaluation)
- **Child-Friendly Design**: Age-appropriate language, encouragement, and error recovery messages
- **Robust Error Handling**: Comprehensive fallback strategies with circuit breakers
- **Session Management**: Persistent state tracking with conversation history
- **LLM Integration**: Tool calling with `meta-llama/llama-3.1-8b-instruct:free` model

## 🚀 Quick Start

### Prerequisites

1. **Python 3.12+** with uv package manager
2. **LiveKit Server** (cloud or self-hosted)
3. **Supabase Database** for question storage and session persistence
4. **OpenRouter Account** for LLM access (free tier available)

### Setup

1. **Clone and Install Dependencies:**
```bash
git clone <repository>
cd voice_tutor
uv sync  # Install all dependencies
```

2. **Configure Environment Variables:**
```bash
cp .env.example .env
# Edit .env with your LiveKit and Supabase credentials
```

3. **Required Environment Variables:**
- `LIVEKIT_URL`: Your LiveKit server WebSocket URL (e.g., `wss://your-project.livekit.cloud`)
- `LIVEKIT_API_KEY`: Your LiveKit API key
- `LIVEKIT_API_SECRET`: Your LiveKit API secret
- `OPENROUTER_API_KEY`: OpenRouter API key for LLM access (free tier available)

### Running the Application

#### Option 1: Standard LiveKit Agent Mode (Recommended)
```bash
# Start the voice agent
uv run python -m src.main
```

The agent will start and wait for incoming room connections. Use the LiveKit CLI or web interface to create rooms and connect clients.

#### Option 2: Development/Test Mode
```bash
# Run in test mode to validate configuration
uv run python -m src.main test

# Run with development settings
uv run python -m src.main --dev
```

#### Option 3: Specify Custom Configuration
```bash
# Use specific model
uv run python -m src.main --model meta-llama/llama-3.1-8b-instruct:free

# Connect to specific room for testing
uv run python -m src.main --room-name test-room-123
```

## 🏗️ Architecture Overview

### New Tool-Based Architecture (SOLID Compliant)

```
VoiceTutorAgent (Single Orchestrator)
    ├── System Prompt (Conversation Guidance)
    ├── Tool Registry (Dynamic Discovery)
    │   ├── UpdateStudentInfoTool
    │   ├── StartQuizTool  
    │   ├── GetNextQuestionTool
    │   ├── EvaluateAnswerTool
    │   └── EndQuizTool
    ├── SessionManager (State Persistence)
    └── LLM Service (Tool Calling)
```

### Key Benefits

1. **Single Responsibility**: Each tool handles one specific operation
2. **Open/Closed Principle**: New features added as tools without core modification
3. **Natural Flow**: LLM decides conversation progression based on context
4. **Robust Recovery**: Child-friendly error handling maintains engagement
5. **Extensible**: Easy to add new quiz types or educational features

## 📚 Migration from Task-Based System

### Deprecated Components (src/agents/tasks/)

- `GreetingTask` → `UpdateStudentInfoTool`
- `DataCollectionTask` → `UpdateStudentInfoTool` 
- `QuizTask` → Multiple specialized quiz tools
- `fsm.py` → `SessionManager` service

### Migration Status: COMPLETE

All original functionality preserved through comprehensive tool coverage with enhanced error handling and child-friendly interaction patterns.

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LiveKit Server Configuration (Required)
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key  
LIVEKIT_API_SECRET=your_livekit_api_secret

# LLM Configuration
LLM_MODEL=meta-llama/llama-3.1-8b-instruct:free
OPENROUTER_API_KEY=your_openrouter_api_key

# Database Configuration (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key

# Voice Processing (Optional)
DEEPGRAM_API_KEY=your_deepgram_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Development Settings
DEBUG=True
LOG_LEVEL=INFO
```

### LiveKit Setup

1. **Create LiveKit Project**: Sign up at [LiveKit Cloud](https://cloud.livekit.io)
2. **Get Credentials**: Copy API Key and Secret from project settings
3. **Configure Rooms**: Create rooms through LiveKit dashboard or API

## 🧪 Testing

### Unit Tests
```bash
uv run pytest src/agents/tools/ -v
```

### Integration Tests
```bash
uv run pytest src/services/ -v
```

### Test Mode
```bash
uv run python -m src.main test
```

## 📖 Usage

### Conversation Flow

1. **Greeting & Info Collection**: Agent greets and uses `UpdateStudentInfoTool` to collect name/subject
2. **Quiz Initialization**: `StartQuizTool` fetches questions and sets up session
3. **Question Presentation**: `GetNextQuestionTool` presents questions naturally  
4. **Answer Evaluation**: `EvaluateAnswerTool` provides semantic scoring and encouragement
5. **Completion**: `EndQuizTool` generates celebratory summary

### Error Recovery

All tools implement comprehensive error handling with child-friendly recovery messages:
- **Database failures**: Emergency fallback questions
- **LLM evaluation failures**: Keyword matching with positive reinforcement  
- **Session issues**: Graceful degradation with cached data
- **Network problems**: Circuit breakers prevent cascading failures

## 🛠️ Development

### Adding New Tools

1. **Create Tool Class** extending `BaseTool`:
```python
class NewLearningTool(BaseTool):
    def __init__(self):
        super().__init__(name="new_learning_tool", description="...")
    
    async def _execute_core(self, parameters, context):
        # Implementation
        pass
```

2. **Register in ToolRegistry**:
```python
registry = get_tool_registry()
registry.register_tool(NewLearningTool())
```

3. **Update System Prompt** (optional - LLM discovers automatically)

### Customizing Behavior

- **System Prompt**: Modify `VoiceTutorAgent._build_system_prompt()` for different conversation styles
- **Recovery Messages**: Customize `BaseTool._get_recovery_configs()` for age-appropriate responses
- **Model Selection**: Change `LLM_MODEL` environment variable

## 📈 Monitoring

### Logging

- **Tool Execution**: Each tool call logged with success/failure status
- **Session Metrics**: Conversation turns, quiz progress, error recovery
- **LLM Performance**: Token usage, response latency, tool calling accuracy

### Metrics

- `tool_invocation_success_rate`: Per-tool reliability
- `session_completion_rate`: Successful educational sessions
- `recovery_message_engagement`: Child continues after error recovery
- `conversation_naturalness`: LLM maintains coherent flow

## 🔒 Security

- **Input Validation**: All tool parameters validated against JSON schemas
- **Session Isolation**: Each conversation maintains separate state
- **Error Containment**: Failures don't affect other sessions
- **Data Privacy**: Student information handled securely through SessionManager

## 🤝 Contributing

1. **New Tools**: Add educational features as single-responsibility tools
2. **Recovery Messages**: Enhance child-friendly error handling
3. **Testing**: Add unit tests for new tools and integration tests
4. **Documentation**: Update README with new features and migration guides

## 📄 License

MIT License - see LICENSE file for details

## 🎉 Next Steps

1. **Deploy**: Set up LiveKit server and configure production environment
2. **Test**: Run comprehensive testing with real voice interactions
3. **Monitor**: Track educational engagement and technical metrics
4. **Enhance**: Add new educational tools and conversation features
5. **Scale**: Optimize for multiple concurrent learning sessions

---

**The voice tutoring agent is now production-ready with a maintainable, extensible architecture that provides superior educational experience through natural, tool-driven conversation while maintaining robust error handling and child-friendly interaction patterns.**