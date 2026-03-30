import chromadb
import os

# Point to your actual folder
db_path = os.path.join(os.getcwd(), "airline_vector_db")
client = chromadb.PersistentClient(path=db_path)

# List all collections to see the exact names
collections = client.list_collections()
print("Available Collections:", [c.name for c in collections])