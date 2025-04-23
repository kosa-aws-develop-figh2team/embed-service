from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

import os
import dotenv
dotenv.load_dotenv()

from utils.save_pgvector import save_text_to_pg, save_chunks_to_pg
from utils.retriever import search_similar_documents, get_embedding_status

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = FastAPI()

# Request & Response Models
class SingleEmbedRequest(BaseModel):
    raw_text: str
    service_id: str

class ChunkEmbedRequest(BaseModel):
    chunk_list: List[str]
    service_id: str

class RetrieveRequest(BaseModel):
    text: str
    top_k: Optional[int] = 5

class EmbedResponse(BaseModel):
    vector_id: str

class ChuckEmbedResponse(BaseModel):
    vector_ids: List[str]
    flag: bool

class RetrieveResponse(BaseModel):
    results: List[dict]

class StatusResponse(BaseModel):
    vector_ids: List[str]
    content: List[str]

@app.get("/health")
def health_check():
    return {"status": "ok"}

# 1. 단일 텍스트 임베딩 생성 및 저장
@app.post("/embed/text", response_model=EmbedResponse)
def embed_single_text(request: SingleEmbedRequest):
    try:
        vector_id = save_text_to_pg(text=request.raw_text, service_id=request.service_id)
        return {"vector_id": vector_id}
    except Exception as e:
        logger.error(f"단일 임베딩 처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="임베딩 처리 중 오류 발생")

# 2. 청크 리스트 임베딩 생성 및 저장
@app.post("/embed/chunks", response_model=ChuckEmbedResponse)
def embed_chunks(request: ChunkEmbedRequest):
    try:
        vector_ids, flag = save_chunks_to_pg(chunks=request.chunk_list, service_id=request.service_id)
        return {"vector_ids": vector_ids, "flag": flag}
    except Exception as e:
        logger.error(f"청크 임베딩 저장 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="청크 임베딩 처리 중 오류 발생")

# 3. 유사 문서 검색
@app.post("/embed/retrieve", response_model=RetrieveResponse)
def retrieve_documents(request: RetrieveRequest):
    try:
        results = search_similar_documents(request.text, top_k=request.top_k)
        return {"results": results}
    except Exception as e:
        logger.error(f"문서 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="문서 검색 중 오류 발생")

# 4. 벡터 저장 상태 조회
@app.get("/embed/status", response_model=StatusResponse)
def get_status(service_id: str = Query(..., description="service_id 값")):
    try:
        status = get_embedding_status(service_id)
        return status
    except Exception as e:
        logger.error(f"상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="상태 조회 중 오류 발생")