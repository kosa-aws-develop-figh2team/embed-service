# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class EmbedRequest(BaseModel):
    raw_text: str

class EmbedResponse(BaseModel):
    embedding_vector: List[float]

@app.post("/embed/text", response_model=EmbedResponse)
def embed_text(request: EmbedRequest):
    # TODO: 추후 모델 삽입
    # 현재는 임시 벡터 반환
    dummy_vector = [0.1, 0.2, 0.3]
    return {"embedding_vector": dummy_vector}