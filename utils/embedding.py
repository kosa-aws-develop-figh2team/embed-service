'''
get_bedrock_embedding, get_korean_embeddings 
    - input : text
    - output : List[float] : 1536
'''

import boto3
import json
import logging
from typing import List
# from transformers import AutoTokenizer, AutoModel
# import torch
from functools import lru_cache

import os
import dotenv
dotenv.load_dotenv()

# Bedrock 모델 설정
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-embed-text-v2:0")
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "ap-northeast-2")

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

@lru_cache()
def get_bedrock_client():
    return boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def get_embeddings(text: str) -> List[float]:
    embedding = get_bedrock_embedding(text)
    return embedding

def get_bedrock_embedding(text: str) -> List[float]:
    """
    Bedrock의 Titan Embedding 모델을 이용해 텍스트 임베딩 생성
    :param text: 청크된 텍스트
    :param model_id: 사용할 embedding 모델 ID
    :param region: Bedrock 리전
    :return: 임베딩 벡터
    """
    logger.info("Bedrock 임베딩 생성 시작")
    client = get_bedrock_client()

    payload = {
        "inputText": text
    }

    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(payload).encode("utf-8"),
        contentType="application/json",
        accept="application/json"
    )

    body = json.loads(response["body"].read().decode("utf-8"))
    embedding = body["embedding"]
    logger.debug(f"임베딩 생성 완료: {embedding}")

    logger.info("Bedrock 임베딩 생성 완료")
    return embedding


# @lru_cache()
def load_model_and_tokenizer():
    pass
#     logger.info("임베딩 모델 및 토크나이저 로딩 시작")
#     tokenizer = AutoTokenizer.from_pretrained("BM-K/KoMiniLM")
#     model = AutoModel.from_pretrained("BM-K/KoMiniLM")
#     logger.info("임베딩 모델 및 토크나이저 로딩 완료")
#     return tokenizer, model

# def get_korean_embeddings(text: str) -> List[float]:
#     logger.info("한국어 임베딩 생성 시작")
#     tokenizer, model = load_model_and_tokenizer()

#     inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
#     with torch.no_grad():
#         embedding = model(**inputs).last_hidden_state[:, 0, :]  # [1, hidden_size]

#     current_dim = embedding.size(1)
#     target_dim = 1536

#     if current_dim < target_dim:
#         pad = torch.zeros((1, target_dim - current_dim), device=embedding.device, dtype=embedding.dtype)
#         padded_embedding = torch.cat([embedding, pad], dim=1)
#     else:
#         padded_embedding = embedding[:, :target_dim]

#     logger.info("한국어 임베딩 생성 완료")
#     return padded_embedding.squeeze(0).tolist()