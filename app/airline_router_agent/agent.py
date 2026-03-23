from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

from app.airline_faq_agent.agent import root_agent as faq_agent
from app.airline_dob_agent.agent import root_agent as dob_agent
from app.airline_flight_agent.agent import root_agent as flight_agent

# async def ask_faq_agent(query: str) -> str:
#     """Use this tool to answer questions about airline policies, baggage, refunds, and check-in."""
#     # This executes the sub-agent's logic and returns its response
#     return await faq_agent.run(query)

# Router Agent 
root_agent = Agent(
    name="airline_router",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction=(
        # "Analyze the user query. "
        # "1. If the user asks about policies, baggage, or refunds, delegate to 'airline_faq_agent'. "
        # "2. For general greetings, be polite and ask how you can help."
        # # "Only give final answer"
        # "If User query is not related to air travel , airport codes ,airline policies, baggage, or refunds, respond with a polite message indicating that you can only assist with those topics."
        "You are the Airline chatbot. Your primary role is to listen to the user and provide solution based on your available functionality"
        "and route them to the most qualified sub-agent: also check tools available for each agent and route accordingly\n"
        "- If they ask about baggage, refunds, or policies -> 'airline_faq_agent'.\n"
        "- If they need to change their birth date or personal info and ask for booking details -> 'airline_dob_agent'.\n"
        "- If they need to modify flights, cities, or travel times -> 'airline_flight_agent'.\n\n"
        "Do not answer these technical questions yourself; always delegate to proper sub-agent."
    ),
    
    # tools=[ask_faq_agent]
    sub_agents=[faq_agent, dob_agent, flight_agent]
)