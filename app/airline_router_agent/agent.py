from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from airline_faq_agent.agent import root_agent as faq_agent

# async def ask_faq_agent(query: str) -> str:
#     """Use this tool to answer questions about airline policies, baggage, refunds, and check-in."""
#     # This executes the sub-agent's logic and returns its response
#     return await faq_agent.run(query)

# Router Agent 
root_agent = Agent(
    name="airline_router",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction=(
        "Analyze the user query. "
        "1. If the user asks about policies, baggage, or refunds, delegate to 'airline_faq_agent'. "
        "2. For general greetings, be polite and ask how you can help."
        "Only give final answer"
    ),
    
    # tools=[ask_faq_agent]
    sub_agents=[faq_agent]
)