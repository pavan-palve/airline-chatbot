import os
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer

# Constants
MODEL_NAME = 'all-MiniLM-L6-v2'
DB_PATH = "./airline_vector_db"
COLLECTION_NAME = "airline_policies"
INPUT_FOLDER = "./Documents"

CHUNK_SIZE = 500      # Target characters per chunk
CHUNK_OVERLAP = 50    # Overlap to prevent context loss

def recursive_splitter(text, separators=["\n\n", "\n", ". ", " ", ""]):
    """
    Recursively splits text into chunks based on a hierarchy of separators.
    """
    chunks = []
    
    def split_text(input_text, current_separators):
        if len(input_text) <= CHUNK_SIZE or not current_separators:
            chunks.append(input_text.strip())
            return

        separator = current_separators[0]
        remaining_separators = current_separators[1:]
        
        # Split by the current separator
        parts = input_text.split(separator)
        current_buffer = ""
        
        for part in parts:
            # If a single part is still too big, recurse deeper
            if len(part) > CHUNK_SIZE:
                if current_buffer:
                    chunks.append(current_buffer.strip())
                    current_buffer = ""
                split_text(part, remaining_separators)
            # Otherwise, build up the buffer
            elif len(current_buffer) + len(part) + len(separator) <= CHUNK_SIZE:
                current_buffer += (separator if current_buffer else "") + part
            else:
                chunks.append(current_buffer.strip())
                current_buffer = part
        
        if current_buffer:
            chunks.append(current_buffer.strip())

    split_text(text, separators)
    
    return [c for c in chunks if len(c) > 20]

def ingest_folder(folder_path):
    print(f"📡 Initializing Embedding Engine: {MODEL_NAME}...")

    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing: {filename}...")
            
            doc = fitz.open(pdf_path)
            full_text = ""
            
            # Combine text first to handle paragraphs spanning across pages
            for page in doc:
                full_text += page.get_text("text") + "\n"
            
            # Apply Recursive Chunking
            chunks = recursive_splitter(full_text)
            
            if not chunks:
                continue

            print(f"Generated {len(chunks)} optimized chunks.")

            embeddings = model.encode(chunks).tolist()
            ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"source": filename, "type": "policy_doc"} for _ in chunks]

            collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )

    print(f"\n✅ Ingestion complete. Index stored at: {DB_PATH}")

if __name__ == "__main__":
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created '{INPUT_FOLDER}'. Please add PDFs and re-run.")
    else:
        ingest_folder(INPUT_FOLDER)