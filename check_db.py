import sqlite3
import os

DB_PATH = os.path.join("airline_sqlite", "airline_db.db")

def run_query(query):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Row factory allows accessing columns by name: row['name']
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            
            rows = cursor.fetchall()
            for row in rows:
                # Convert row to a dictionary for easy printing
                print(dict(row))
    except Exception as e:
        print(f"Error: {e}")

while True:
    print(">>")
    query=input()
    run_query(query)

