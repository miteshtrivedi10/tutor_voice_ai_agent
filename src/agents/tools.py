"""
Stateless tools for voice agent tasks.
Uses RunContext for session access and MCP for external resources.
"""

from typing import Any, Annotated
from livekit.agents import function_tool, get_job_context, ToolError
from livekit.agents.voice import RunContext
from livekit.api import DeleteRoomRequest
from src.config.logging_config import logger
from src.services.usage_service import UsageService
from src.models.agent_dtos import UsageMetrics


@function_tool
async def end_the_call(ctx: RunContext, message: str) -> None:
    """End the call and delete the room."""
    session = ctx.session
    await session.say(
        "Good bye! This call will now get disconnected", allow_interruptions=False
    )
    job_ctx = get_job_context()
    job_ctx.shutdown()
    await job_ctx.api.room.delete_room(DeleteRoomRequest(room=job_ctx.room.name))


@function_tool
async def update_student_name(
    ctx: RunContext, student_name: Annotated[str, "The student's name"]
) -> str:
    """Update student name using RunContext."""
    session = ctx.session
    session.userdata.student_name = student_name
    logger.info(f"Updating student name to: {student_name}")
    return "Alright, I've updated the name."


@function_tool
async def update_subject(
    ctx: RunContext, subject: Annotated[str, "Student's chosen subject"]
) -> str:
    """Update subject using RunContext."""
    session = ctx.session
    session.userdata.subject = subject
    logger.info(f"Updating subject to: {subject}")
    return "Alright, I've updated the subject."


@function_tool
async def start_quiz(ctx: RunContext, message: str) -> str:
    """Start quiz using MCP for Supabase query."""
    session = ctx.session
    session_data = session.userdata
    stud_name = session_data.student_name
    sub = session_data.subject

    if stud_name == "Student name is Missing. Required" or not stud_name:
        raise ToolError("Invalid student name. Please update first.")
    if sub == "Subject is missing. Required" or not sub:
        raise ToolError("Invalid subject. Please update first.")

    try:
        # Use MCP for Supabase query
        from livekit.agents import use_mcp_tool

        result = await use_mcp_tool(
            server_name="supabase-mcp",
            tool_name="execute_sql",
            arguments={
                "query": f"SELECT id, question, answer FROM questions WHERE subject = '{sub}' ORDER BY RANDOM() LIMIT 10;"
            },
        )
        # Assume result is list of dicts
        assessments = result["rows"] if "rows" in result else []
        # Process assessments as before
        if assessments:
            values = [row["answer"] for row in assessments]  # Assume structure
            import pandas as pd

            value_counts = pd.Series(values).value_counts()
            results_summary = value_counts.to_dict()
        else:
            results_summary = "No questions available."

        await session.generate_reply(
            instructions=f"Quiz completed! Results: {results_summary}. End the call.",
            allow_interruptions=False,
        )
        await end_the_call(ctx, "Quiz ended")
        return "Quiz started and completed successfully."
    except Exception as e:
        raise ToolError(f"Quiz start failed: {str(e)}")
