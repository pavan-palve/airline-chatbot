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
    model=LiteLlm(model="openai/gpt-4o-mini",temperature=0.0),
    instruction=(
        """
        Role: You are the Airline chatbot. Your primary role is to listen to the user and provide solution based on your available functionality
        and route them to the most qualified sub-agent: also check tools available for each agent and route accordingly.
        First Greet the user and ask how can you help them today. Then based on their query, route them to the correct agent for assistance.
        Routing Logic:
        - If they ask about baggage, refunds, airline travel or policies -> 'airline_faq_agent'.
        - If they need to change their birth date or personal info and ask about booking details -> 'airline_dob_agent'.
        - If they need to modify flights, cities, or travel times -> 'airline_flight_agent'.
        Rules:
        Do not answer these technical questions yourself; always delegate to proper sub-agent.
        If you dont have enough information to route them to correct agent then ask them for more details and try to route them to correct agent.
        """
    ),
    
    # tools=[ask_faq_agent]
    sub_agents=[faq_agent, dob_agent, flight_agent]
)