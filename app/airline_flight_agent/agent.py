import requests
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from typing import Optional

API_BASE = "http://127.0.0.1:8001/api"

# Get the flight details for a given pnr
def check_current_flight(pnr: str):
    """Usage: Retrieves existing flight info for the PNR."""
    res = requests.get(f"{API_BASE}/passenger/{pnr}")
    return res.json() if res.status_code == 200 else "PNR not found."

# Search avaialbale flights bases on user preferences
# def find_flights(departure: str, destination: str, date: str):
#     """Usage: Checks availability and route validity in the schedule."""
#     params = {"departure": departure, "destination": destination, "date": date}
#     res = requests.get(f"{API_BASE}/flight/search", params=params)
#     return res.json()

def find_flights(
    departure: Optional[str] = None, 
    destination: Optional[str] = None, 
    date: Optional[str] = None
):
    """Usage: Checks availability and route validity in the schedule."""
    
    raw_params = {
        "departure": departure,
        "destination": destination,
        "date": date
    }
    params = {k: v for k, v in raw_params.items() if v is not None}
    
    res = requests.get(f"{API_BASE}/flight/search", params=params)
    return res.json()

# Commit the flight change request in db
def commit_flight_change(pnr: str, passenger_id: str, new_flight_number: str):
    """Usage: Modifies the flight number/destination for a passenger."""
    payload = {"passenger_id": passenger_id, "new_flight_number": new_flight_number}
    res = requests.put(f"{API_BASE}/flight/{pnr}/details", json=payload)
    return res.json()

root_agent = Agent(
    name="airline_flight_agent",
    model=LiteLlm(model="openai/gpt-4o-mini",temperature=0.1),
    instruction=(
        """
        You are the Flight Modification Specialist. You handle changes to cities, dates, and times by switching flight numbers.
        1. Use 'check_current_flight' to see what the user currently has booked.
        2. If they want to change a city or date, use 'find_flights' to search for alternatives.
        3. Present options (Flight #, Time, Route) to the user. 
        Note: 'find_flights' has optional parameters to narrow down the search based on user preferences. It can also search all flights if called without specifying parameters. 
        If the user is unsure about available flights, provide options based on their preferences (e.g., departure location, destination, and date of travel). Even if the user provides no specific preferences, suggest alternatives by searching for available flights based on their current booking details.
        Always check for timing conflicts before booking a new flight; there should be no overlap between the new flight and the user's existing itinerary.
        4. If the user agrees, use 'commit_flight_change' to finalize the change. Validate all inputs with the user before calling this tool.
        Important: Do not modify data for the first passenger by default if there are multiple passengers in the same PNR. Always ask for the specific Passenger ID and validate it before making any changes.
        """
    ),
    tools=[check_current_flight, find_flights, commit_flight_change]
)