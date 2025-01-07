from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import List

app = FastAPI()

# Load the model once when server starts
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class TextInput(BaseModel):
    text: str

@app.post("/embed")
async def create_embedding(input: TextInput) -> List[float]:
    # Generate embedding
    embedding = model.encode(input.text)
    # Convert to regular float for JSON serialization
    return embedding.tolist()