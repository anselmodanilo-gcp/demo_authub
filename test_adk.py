import asyncio
from google.adk import Agent, Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

def my_tool(x: int) -> int:
    return x * 2

agent = Agent(name="test", model="gemini-2.5-flash", tools=[my_tool])
runner = Runner(app_name="test_app", agent=agent, session_service=InMemorySessionService(), auto_create_session=True)

async def main():
    # Wait, the signature of run_async is:
    # run_async(self, *, user_id: 'str', session_id: 'str', new_message: 'types.Content', state_delta: 'Optional[dict[str, Any]]' = None, run_config: 'Optional[RunConfig]' = None)
    
    msg = Content(parts=[Part.from_text(text="Use my_tool with x=5")])
    async for event in runner.run_async(user_id="u1", session_id="s1", new_message=msg):
        print(event.message)

asyncio.run(main())
