# Voice Tutor Agent 🎙️🎓

A next-generation, real-time voice tutoring assistant that interacts with students using natural language. Built with a decoupled microservices architecture, it leverages **LiveKit** for ultra-low latency voice streaming and the **Model Context Protocol (MCP)** for robust, scalable business logic and semantic evaluation.

## 🌟 Key Features

- **Real-Time Voice Interaction:** Delivers seamless Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities using LiveKit, Deepgram, Groq, and Silero VAD for intelligent turn detection.
- **Semantic Answer Evaluation:** Moving beyond rigid exact-match scoring, the tutor evaluates open-ended student answers using Semantic Similarity (Sentence Transformers) to truly understand the student's intent.
- **Decoupled Architecture:** Clean separation of concerns between the real-time audio pipeline and the underlying knowledge/evaluation engine.
- **High Performance:** Employs in-memory caching (`Theine`) to instantly serve quiz questions and evaluate answers, minimizing database latency during active sessions.
- **Cloud-Native Storage:** Fully integrated with Supabase to store quizzes, subjects, user profiles, and historical session states.

## 🏗️ Architecture & Project Structure

The project is split into two independent but cooperating services:

### 1. `agent_code/` (The Voice Agent)
The conversational frontend that manages the real-time audio and agent states.
- **Tech Stack:** Python 3.12, LiveKit Agents framework, Deepgram (STT), Groq (LLM for fast inference), Silero (VAD).
- **Highlights:** 
  - `tutor_agent.py`: Handles session initialization, user presence detection, and subject selection.
  - `run_quiz_agent.py`: Orchestrates the actual quiz flow, managing conversational turns, asking questions, and gracefully ending the session.
  - **Observability:** Built-in OpenTelemetry for detailed metrics and distributed tracing.

### 2. `mcp_code/` (The MCP Server)
The intelligence backend that exposes tools and knowledge to the Voice Agent via the Model Context Protocol (FastMCP).
- **Tech Stack:** Python 3.12, FastMCP, FastAPI, Supabase client, Sentence Transformers.
- **Highlights:** 
  - Runs a streamable HTTP endpoint (`/mcp_server`).
  - **Tool Set:** Exposes critical functions to the LLM agent including `get_valid_subjects_to_choose_from`, `start_quiz`, `get_quiz_question`, and `evaluate_student_answer`.
  - **AI Evaluation:** Analyzes student responses dynamically against the correct answers using semantic embeddings to generate a similarity score.

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- Supabase project for data storage
- API Keys for LiveKit, Deepgram, and Groq

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd voice_tutor
   ```

2. **Environment Configuration:**
   You will need to set up environment variables in both service directories. Look for `.env.example` or refer to `src/config/settings.py` in each directory.
   Expected keys generally include:
   - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
   - `DEEPGRAM_API_KEY`, `GROQ_API_KEY`
   - `SUPABASE_URL`, `SUPABASE_KEY`

3. **Start the MCP Server:**
   The knowledge and evaluation backend must be running for the agent to access its tools.
   ```bash
   cd mcp_code
   pip install -e .
   python -m src.main
   ```

4. **Start the Voice Agent:**
   In a separate terminal, launch the conversational agent.
   ```bash
   cd agent_code
   pip install -e .
   python -m src.main
   ```

## 🧪 Testing

Both components have their own test suites. To run tests, navigate to the respective directory and run:

```bash
pytest tests/
```
