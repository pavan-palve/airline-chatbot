import os
import chromadb
from sentence_transformers import SentenceTransformer
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm 


# DB_PATH = "./../airline_vector_db" # Path to your created embeddings
# COLLECTION_NAME = "airline_policies"

# 1. Initialize RAG Knowledge Base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "airline_vector_db")
COLLECTION_NAME = "airline_policies"

embed_model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_collection(name=COLLECTION_NAME)

# collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# 2. Define the Retrieval Function --> passed as tool in root_agent
def search_airline_policy(query: str) -> str:
    """Searches the airline baggage, check-in, and refund policies from the RAG Knowledge base."""
    query_vector = embed_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2
    )
    if results['documents']:
        return " ".join(results['documents'][0])
    return "I couldn't find a specific policy for that."

model_instance = LiteLlm(model="openai/gpt-4o-mini",temperature=0.1)

# 3. Define the Root Agent
root_agent = Agent(
    name="airline_faq_agent",
    model=model_instance,  # ADK will use ChatGPT model 
    instruction=(
        """
        You are an intelligent airline faq agent.
        Your task is to assist users with questions about airline policies, including baggage rules, check-in procedures, and refund policies.
        Use the 'search_airline_policy' tool to look up rules and policies in the airline knowledge base when users ask related questions.
        Dont answer these technical questions yourself; always use the tool to get accurate and up-to-date information.
        Please provide clear and concise answers with proper points to user queries about airline policies.
        """
    ),
    tools=[search_airline_policy] # Equipping the agent with tools
)