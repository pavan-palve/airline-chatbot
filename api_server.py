import os
import sqlite3
from fastapi import FastAPI, HTTPException 
from fastapi import Query
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="Airline Chatbot")

# Configuration to create sqlite db
DB_FOLDER = "airline_sqlite"
DB_NAME = "airline_db.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

SQL_INIT_FILE = "init.sql" # Initialize db with bookings , flight and passenger table with pre existing mock data

# Required object fot dob update api as payload
class DOBUpdateRequest(BaseModel):
    passenger_id: str  # Needed because one PNR can have multiple passengers
    new_dob: str       # Format: YYYY-MM-DD

# Required object for flight change api as payload
class FlightChangeRequest(BaseModel):
    passenger_id: str
    new_flight_number: str


def initialize_db():
    """
    Initializes the SQLite database using the SQL script in init.sql with pre-existing mock data.
    """
    # Ensure the database folder exists
    os.makedirs(DB_FOLDER, exist_ok=True)

    # Connect to the SQLite database (it will be created if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)

    try:
        # Read the SQL initialization script
        with open(SQL_INIT_FILE, 'r') as sql_file:
            sql_script = sql_file.read()

        # Execute the SQL script
        conn.executescript(sql_script)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")
    finally:
        # Close the database connection
        conn.close()

@app.get("/api/passenger/{pnr}")
async def get_passenger_details(pnr: str):
    """Usage: Get booking details via PNR lookup"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Returns results as dictionaries
        cursor = conn.cursor()
        
        # Get passenger and flight details for the given PNR
        query = """
            SELECT p.id, p.name, p.dob, f.flight_number, f.departure, 
                   f.destination, f.date, f.time
            FROM passengers p
            JOIN flights f ON p.flight_number = f.flight_number
            WHERE p.pnr = ?
        """
        # ? is a placeholder for parameterized query to prevent SQL injection and pnr.upper() ensures case-insensitive lookup
        cursor.execute(query, (pnr.upper(),))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"Booking {pnr} not found")
        
        # Constructing the nested JSON structure
        passengers = []
        for row in rows:
            passengers.append({
                "id": row["id"],
                "name": row["name"],
                "dob": row["dob"],
                "flight": {
                    "number": row["flight_number"],
                    "departure": row["departure"],
                    "destination": row["destination"],
                    "date": row["date"],
                    "time": row["time"]
                }
            })
            
        return {
            "pnr": pnr.upper(),
            "passengers": passengers
        }
    
# Using Query parameters as this payload expects optional arguments
@app.get("/api/flight/search")
async def search_flights(
    departure: Optional[str] = Query(None, description="Origin Airport Code (e.g., NAG)"),
    destination: Optional[str] = Query(None, description="Destination Airport Code (e.g., BOM)"),
    date: Optional[str] = Query(None, description="Travel Date (YYYY-MM-DD)")
):
    """Usage: Search available flights based on route and date"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Base query
        query = "SELECT * FROM flights WHERE 1=1"
        params = []
        
        # Dynamic filtering based on user input
        if departure:
            query += " AND departure = ?"
            params.append(departure.upper())
        if destination:
            query += " AND destination = ?"
            params.append(destination.upper())
        if date:
            query += " AND date = ?"
            params.append(date)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert rows to a list of flight objects
        flights = []
        for row in rows:
            flights.append({
                "number": row["flight_number"],
                "departure": row["departure"],
                "destination": row["destination"],
                "date": row["date"],
                "time": row["time"]
            })
            
        return {"results_count": len(flights), "flights": flights}

# API to update the passenger details ( DOB ) with PNR and DOBUpdateRequest object ( passenger id and new DOB)
@app.put("/api/passenger/{pnr}/dob")
async def update_passenger_dob(pnr: str, request: DOBUpdateRequest):
    """Requirement: Update a passenger's Date of Birth"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # 1. Verify the passenger exists for this specific PNR
        cursor.execute(
            "SELECT id FROM passengers WHERE pnr = ? AND id = ?", 
            (pnr.upper(), request.passenger_id.upper())
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404, 
                detail=f"Passenger {request.passenger_id} not found in booking {pnr}"
            )
        
        # 2. Perform the update
        cursor.execute(
            "UPDATE passengers SET dob = ? WHERE pnr = ? AND id = ?",
            (request.new_dob, pnr.upper(), request.passenger_id.upper())
        )
        conn.commit()
        
        return {
            "status": "success",
            "message": f"DOB for {request.passenger_id} updated to {request.new_dob}",
            "pnr": pnr.upper()
        }

@app.put("/api/flight/{pnr}/details")
async def change_passenger_flight(pnr: str, request: FlightChangeRequest):
    """Usage: Update flight details for a specific booking"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Verify the new flight exists in our schedule
        cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (request.new_flight_number.upper(),))
        new_flight = cursor.fetchone()
        if not new_flight:
            raise HTTPException(status_code=404, detail=f"Flight {request.new_flight_number} not found in schedule")

        # 2. Update the passenger's flight reference
        cursor.execute(
            "UPDATE passengers SET flight_number = ? WHERE pnr = ? AND id = ?",
            (request.new_flight_number.upper(), pnr.upper(), request.passenger_id.upper())
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Booking or Passenger ID mismatch")
            
        conn.commit()

        # 3. Fetch updated info to give the Agent context for the "Success" message
        cursor.execute("SELECT name FROM passengers WHERE id = ?", (request.passenger_id.upper(),))
        pax_name = cursor.fetchone()["name"]

        return {
            "status": "success",
            "message": f"Flight changed to {new_flight['flight_number']}",
            "details": {
                "passenger": pax_name,
                "flight_no": new_flight["flight_number"],
                "origin": new_flight["departure"],
                "destination": new_flight["destination"],
                "time": new_flight["time"]
            }
        }

if __name__ == "__main__":
    initialize_db()
    print(f"Database ready at: {DB_PATH}")
    uvicorn.run(app, host="127.0.0.1", port=8001)