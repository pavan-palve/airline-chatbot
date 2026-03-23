import requests
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

API_BASE = "http://127.0.0.1:8001/api"

def get_booking(pnr: str):
    """Usage: Checks if PNR is valid and exists in system."""
    res = requests.get(f"{API_BASE}/passenger/{pnr}")
    return res.json() if res.status_code == 200 else f"Error: {res.json()['detail']}"

def update_dob(pnr: str, passenger_id: str, new_dob: str):
    """Usage: Updates DOB. Expected format: YYYY-MM-DD."""
    payload = {"passenger_id": passenger_id, "new_dob": new_dob}
    res = requests.put(f"{API_BASE}/passenger/{pnr}/dob", json=payload)
    return res.json()

root_agent = Agent(
    name="airline_dob_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    instruction=(
        "You are the DOB Specialist. Your only purpose is to update passenger birth dates.\n"
        "1. Ask for PNR and Passenger ID (e.g., PAX001) if not provided.\n"
        "2. Use 'get_booking' to verify the record exists. this function needs to be called with the PNR \n"
        "3. Use 'update_dob' to commit the change. Ensure the DOB is in YYYY-MM-DD format. this function requires the PNR, Passenger ID, and new DOB as arguments\n"
        "4. Confirm the update with the new details to the user."
    ),
    tools=[get_booking, update_dob]
)