import os
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = 'all-MiniLM-L6-v2'
DB_PATH = "./airline_vector_db"  # Path of vector db storage
COLLECTION_NAME = "airline_policies"
INPUT_FOLDER = "./Documents"

def ingest_folder(folder_path):
    print(f"Starting with Embedding Creation with model : {MODEL_NAME}...")

    # Set Model for Embedding and create a croma db collection
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"} # Using cosine as per the requirements
    )

    # Looping through all the pdf files in the Document folder 
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):       # filtering files with pdf extension
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}...")
            
            # Extract text from the current PDF
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                
                # Chunking: Split by double newlines for paragraph-level retrieval
                paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 40]
                
                if not paragraphs:
                    continue

                # Generate embeddings for this page's chunks
                embeddings = model.encode(paragraphs).tolist()
                
                # Metadata helps the agent identify which document the info came from
                ids = [f"{filename}_p{page_num}_{i}" for i in range(len(paragraphs))]
                metadatas = [{"source": filename, "page": page_num} for _ in paragraphs]

                # Add to the mock vector database (Phase 2, Item 1)
                collection.add(
                    documents=paragraphs,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )

    print(f"\nIngestion complete. All PDFs in '{folder_path}' are now indexed in {DB_PATH}.")

if __name__ == "__main__":
    # Create the folder if it doesn't exist for testing
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created '{INPUT_FOLDER}' folder. Please drop your PDFs there and run again.")
    else:
        ingest_folder(INPUT_FOLDER)