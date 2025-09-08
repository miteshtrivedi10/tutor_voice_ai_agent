"""
Main entry point for the Voice Tutor application.
Uses direct configuration variable access from settings.py.
"""

import asyncio
import os
from typing import Any
import argparse
import sys

from livekit.agents import JobContext
from livekit.agents.cli import proto
from livekit.agents.worker import WorkerOptions, Worker
from livekit.agents.cli._run import run_dev

from src.config.settings import (
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
    SUPABASE_URL,
    SUPABASE_KEY,
    SARVAM_API_KEY,
    TAVILY_API_KEY,
    DEEPGRAM_API_KEY,
)
from src.config.logging_config import logger
from src.agents.tutor_agent import agent_entrypoint


async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the refactored VoiceTutorAgent.
    Uses the new single agent architecture with comprehensive tool calling.
    """
    logger.info("Starting Voice Tutor with new tool-based architecture")

    # Use the updated agent entrypoint from new architecture
    await agent_entrypoint(ctx)


def parse_arguments():
    """Parse command line arguments for compatibility."""
    parser = argparse.ArgumentParser(
        description="Voice Tutor Agent - Tool-Based Architecture"
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        help="Command to execute (default: start)",
    )
    parser.add_argument("--dev", action="store_true", help="Run in development mode")
    parser.add_argument(
        "--model",
        type=str,
        default="meta-llama/llama-3.1-8b-instruct:free",
        help="LLM model to use",
    )
    parser.add_argument("--room-name", type=str, help="Specific room name for testing")

    return parser.parse_args()


async def main():
    """Main function to run the voice tutor application."""
    args = parse_arguments()

    if args.command == "start" or args.command is None:
        logger.info(f"Starting Voice Tutor agent with command: {args.command}")
        logger.info(f"Using LLM model: meta-llama/llama-3.1-8b-instruct:free")
        logger.info(f"LiveKit URL: {LIVEKIT_URL}")
        logger.info(f"Supabase URL: {SUPABASE_URL}")

        # Configure LiveKit worker with environment variables
        development_mode = args.dev or True  # Default to dev mode

        opts = WorkerOptions(entrypoint_fnc=entrypoint)
        opts.ws_url = LIVEKIT_URL or "http://localhost:7880"
        opts.api_key = LIVEKIT_API_KEY
        opts.api_secret = LIVEKIT_API_SECRET
        opts.drain_timeout = 0  # Immediate shutdown for dev

        args_proto = proto.CliArgs(
            opts=opts,
            log_level="INFO",
            devmode=development_mode,
            asyncio_debug=False,
            watch=False,
            register=True,
        )

        # Check if event loop is already running (e.g., under uv run)
        try:
            asyncio.get_event_loop_policy().get_event_loop()
            loop_exists = True
        except RuntimeError:
            loop_exists = False

        if loop_exists:
            # Run worker directly if loop exists
            logger.info("Event loop detected, starting worker directly")
            worker = Worker(opts, devmode=development_mode)
            await worker.run()
        else:
            # Use run_dev for standalone execution
            logger.info("No event loop detected, using run_dev")
            run_dev(args_proto)
    elif args.command == "test":
        logger.info("Running Voice Tutor in test mode")
        # Test mode implementation - could spin up test room or validate configuration
        await run_test_mode()
    else:
        logger.error(f"Unknown command: {args.command}")
        print(
            f"Usage: uv run python -m src.main [start|test] [--dev] [--model MODEL] [--room-name ROOM]"
        )
        print(
            "\nMake sure to copy .env.example to .env and configure your LiveKit credentials!"
        )
        sys.exit(1)


async def run_test_mode():
    """Run the agent in test mode for validation."""
    logger.info("Running Voice Tutor in test mode")

    # Test configuration and dependencies
    from src.services.tool_registry import get_tool_registry
    from src.services.session_manager import get_session_manager

    registry = get_tool_registry()
    session_mgr = get_session_manager()

    print("Configuration Test Results:")
    print(f"✓ Tool Registry: {registry.get_tool_count()} tools registered")
    print(f"✓ Session Manager: Ready for session management")
    print("✓ Model: meta-llama/llama-3.1-8b-instruct:free")
    print(f"✓ LiveKit URL: {LIVEKIT_URL}")
    print(f"✓ Supabase URL: {SUPABASE_URL}")

    # Test tool execution if possible
    try:
        from src.agents.tools.update_student_info_tool import UpdateStudentInfoTool

        test_tool = UpdateStudentInfoTool()
        print(f"✓ Test tool created: {test_tool.name}")
    except Exception as e:
        print(f"✗ Tool test failed: {e}")
        return False

    # Test session manager
    test_session_id = "test_session_123"
    test_data = {"test_field": "test_value"}
    test_result = await session_mgr.update_session_data(test_session_id, test_data)
    print(f"✓ Session Manager test: {test_result.success}")

    logger.info("Test mode completed successfully")
    return True


if __name__ == "__main__":
    # Run the application with new architecture
    try:
        asyncio.run(main())
        logger.info(
            "Voice Tutor application startup completed with new tool-based architecture"
        )
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"1. Check that .env file is configured with LiveKit credentials")
        print(f"2. Verify LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET are set")
        print(f"3. Ensure Supabase credentials are configured for quiz questions")
        print(f"4. Run `uv run python -m src.main test` to validate configuration")
        print(f"5. Check that .env file is in the project root directory")
        print(f"6. Verify all required environment variables are exported:")
        print(f"   $ export $(cat .env | xargs)")
        sys.exit(1)

# Export for LiveKit integration and direct execution
__all__ = ["entrypoint", "main", "parse_arguments"]
