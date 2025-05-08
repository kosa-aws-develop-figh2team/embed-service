from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

import os
import dotenv
dotenv.load_dotenv()

from utils.save_pgvector import save_text_to_pg, save_chunks_to_pg
from utils.retriever import search_similar_documents, get_embedding_status
from utils.dynamodb_logger import update_metadata

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
        # 상태 업데이트: 임베딩 시작
        update_metadata(
            service_id=request.service_id,
            step="embedding",
            status="in_progress"
        )

        vector_id = save_text_to_pg(text=request.raw_text, service_id=request.service_id)

        # 상태 업데이트: 임베딩 완료
        update_metadata(
            service_id=request.service_id,
            step="embedding",
            status="completed",
            vector_ids=[vector_id]
        )

        return {"vector_id": vector_id}
    except Exception as e:
        # 상태 업데이트: 실패
        update_metadata(
            service_id=request.service_id,
            step="embedding",
            status="failed",
            error=str(e)
        )
        logger.error(f"단일 임베딩 처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="임베딩 처리 중 오류 발생")


# 2. 청크 리스트 임베딩 생성 및 저장 (비동기 + 실패 핸들링 추가)
def save_chunks_background(chunks: List[str], service_id: str):
    try:
        update_metadata(
            service_id=service_id,
            step="embedding",
            status="in_progress"
        )

        logger.info(f"✅ 백그라운드로 청크 저장 시작: service_id={service_id}, 청크 수={len(chunks)}")
        vector_ids, flag = save_chunks_to_pg(chunks=chunks, service_id=service_id)

        update_metadata(
            service_id=service_id,
            step="embedding",
            status="completed",
            vector_ids=vector_ids
        )

        logger.info(f"✅ 백그라운드로 청크 저장 완료: service_id={service_id}, 저장된 벡터 수={len(vector_ids)}")
    except Exception as e:
        update_metadata(
            service_id=service_id,
            step="embedding",
            status="failed",
            error=str(e)
        )
        logger.error(f"❌ 백그라운드 청크 저장 실패: service_id={service_id}, 에러={str(e)}")
    
# # 2. 청크 리스트 임베딩 생성 및 저장
# @app.post("/embed/chunks", response_model=ChuckEmbedResponse)
# def embed_chunks(request: ChunkEmbedRequest):
#     try:
#         vector_ids, flag = save_chunks_to_pg(chunks=request.chunk_list, service_id=request.service_id)
#         return {"vector_ids": vector_ids, "flag": flag}
#     except Exception as e:
#         logger.error(f"청크 임베딩 저장 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail="청크 임베딩 처리 중 오류 발생")

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