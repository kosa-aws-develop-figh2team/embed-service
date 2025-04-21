# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from embedding import get_korean_embeddings

app = FastAPI()

class EmbedRequest(BaseModel):
    raw_text: str

class EmbedResponse(BaseModel):
    embedding_vector: List[float]

@app.post("/embed/text", response_model=EmbedResponse)
def embed_text(request: EmbedRequest):
    raw_text = request.raw_text
    vector = get_korean_embeddings(raw_text)
    return {"embedding_vector": vector}