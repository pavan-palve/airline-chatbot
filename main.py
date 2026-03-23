import os
import sys
import subprocess
import uvicorn
import signal
from google.adk.cli.fast_api import get_fast_api_app

AGENT_HOME = os.path.join(os.getcwd(), "app")
DB_URL = "sqlite+aiosqlite:///airline_sqlite/airline_db.db"

app = get_fast_api_app(
    agents_dir=AGENT_HOME,
    session_service_uri=DB_URL,
    web=True  # Enables the Dev UI at http://127.0.0.1:8000
)

if __name__ == "__main__":
    print(f"Starting API Server (api_server.py) on port 8001...")
    api_process = subprocess.Popen([sys.executable, "api_server.py"])
    print(f"Airline Chatbot: {AGENT_HOME}")
    print(f"📁 Session DB: {DB_URL}")
    uvicorn.run(app, host="127.0.0.1", port=8000)