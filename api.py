from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Importing your existing functions!
# (Make sure the import names match your exact file names)
from database import load_mysql_data
from vectorstore import create_vectorstore  # Note: adjust if your file is named "vector store.py"
from ragapp import rag_answer

app = FastAPI()

# CRITICAL: This allows your TypeScript frontend to talk to this Python API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change "*" to your frontend URL (e.g., "http://localhost:3000")
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to hold our vector store
vector_store = None


# This runs once when you start the server to load the DB and Vectors
@app.on_event("startup")
def startup_event():
    global vector_store
    try:
        print("Connecting to DB and initializing Vector Store...")
        df = load_mysql_data()
        vector_store = create_vectorstore(df)
        print(f"✅ Vector store loaded successfully with {len(df)} records!")
    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")


# This defines what the JSON request from your frontend will look like
class ChatRequest(BaseModel):
    question: str


# This is the endpoint your frontend will call
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if vector_store is None:
        raise HTTPException(status_code=500, detail="Vector store not initialized. Check your DB or API Key.")

    try:
        # Calls your existing LangChain logic
        answer = rag_answer(vector_store, request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))