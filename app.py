from fastapi import FastAPI
import chromadb
import ollama
import os
import logging

logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s-%(levelname)s-%(message)s",
)

MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
logging.info(f"Using model: {MODEL_NAME}")

app = FastAPI()
chroma = chromadb.PersistentClient(path="./db")
collection = chroma.get_or_create_collection("docs")

@app.post("/query")
def query(q: str):
    results = collection.query(query_texts=[q], n_results=1)
    context = results["documents"][0][0] if results["documents"] else ""

    answer = ollama.generate(
        model=MODEL_NAME,
        prompt=f"Context:\n{context}\n\nQuestion: {q}\n\nAnswer clearly and concisely:"
    )
    
    logging.info(f"/query asked: {q}")
    return {"answer": answer["response"]}

@app.post("/add")
def add_knowledge(text: str):
    """Add new content to the knowlage base dynamically"""
    try:
        import uuid
        doc_id = str(uuid.uuid4())
        
        collection.add(documents=[text], ids=[doc_id])
        
        logging.info(f"/add received new txt (id will be genearated: {doc_id})")
        return {
            "stats": "success",
            "message": "Content added to knowladge base",
            "id": doc_id
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        
@app.get("/health")
def health_ckeck():
    """Chaecks the health of the API"""
    return {
        "stats": "OK"
    }