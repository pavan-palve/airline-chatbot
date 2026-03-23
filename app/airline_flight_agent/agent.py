import requests
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

API_BASE = "http://127.0.0.1:8001/api"

# Get the flight details for a given pnr
def check_current_flight(pnr: str):
    """Usage: Retrieves existing flight info for the PNR."""
    res = requests.get(f"{API_BASE}/passenger/{pnr}")
    return res.json() if res.status_code == 200 else "PNR not found."

# Search avaialbale flights bases on user preferences
def find_flights(departure: str, destination: str, date: str):
    """Usage: Checks availability and route validity in the schedule."""
    params = {"departure": departure, "destination": destination, "date": date}
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
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction=(
        "You are the Flight Modification Specialist. You handle changes to cities, "
        "dates, and times by switching flight numbers.\n"
        "1. Use 'check_current_flight' to see what the user currently has booked.\n"
        "2. If they want to change a city or date, use 'find_flights' to search for alternatives.\n"
        "3. Present options (Flight #, Time, Route) to the user. \n"
        "If user dont know about the available flight give him options based on his preference. like his departure location , destination and date of travel."
        "even he knows nothing suggest him by searching available flights based on his current flight details."
        "Also check if there are any timing conflicts also before booking new flight for passenger , there should not be any overlap in timings of new flight with existing flight. \n"
        "4. If they agree, use 'commit_flight_change' to finalize. Validate all inputs before calling from the user."
    ),
    tools=[check_current_flight, find_flights, commit_flight_change]
)