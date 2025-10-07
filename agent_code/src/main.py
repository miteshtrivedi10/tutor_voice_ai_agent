"""
Main entry point for the voice agent application
"""

from livekit import agents

from .tutor_agent import agent_entrypoint

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=agent_entrypoint))
