import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from app.agent import root_agent
from google.genai import types as genai_types


async def main():
    """Runs the agent with a sample query."""
    session_service = InMemorySessionService()
    session_id = "test_session_multi_turn"
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id=session_id
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )

    # Turn 1: Set the project ID
    project_id = "gauss--core--dev--af"
    print(f"--- Setting project ID to {project_id} ---")
    query1 = f"set project id to {project_id}"
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session_id,
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query1)]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)

    # Turn 2: Analyze the infrastructure
    print("\n--- Analyzing infrastructure ---")
    query2 = "analyze infrastructure"
    async for event in runner.run_async(
        user_id="test_user",
        session_id=session_id,
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=query2)]
        ),
    ):
        if event.is_final_response():
            print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())