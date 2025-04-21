# import boto3
import json
import logging
from typing import List

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_bedrock_embedding(text: str, model_id="amazon.titan-embed-text-v1", region="us-west-2") -> List[float]:
    """
    Bedrock의 Titan Embedding 모델을 이용해 텍스트 임베딩 생성
    :param text: 청크된 텍스트
    :param model_id: 사용할 embedding 모델 ID
    :param region: Bedrock 리전
    :return: 임베딩 벡터
    """
    logger.info("Bedrock 임베딩 생성 시작")
    client = boto3.client("bedrock-runtime", region_name=region)

    payload = {
        "inputText": text
    }

    response = client.invoke_model(
        modelId=model_id,
        body=json.dumps(payload).encode("utf-8"),
        contentType="application/json",
        accept="application/json"
    )

    body = json.loads(response["body"].read())
    embedding = body["embedding"]
    logger.debug(f"임베딩 생성 완료: {embedding}")

    logger.info("Bedrock 임베딩 생성 완료")
    return embedding

# 임시 모델
from transformers import AutoModel, AutoTokenizer
import torch


def get_korean_embeddings(text: str) -> List[float]:
    logger.info("한국어 임베딩 생성 시작")
    tokenizer = AutoTokenizer.from_pretrained('BM-K/KoSimCSE-roberta')
    model = AutoModel.from_pretrained('BM-K/KoSimCSE-roberta')
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        embedding = model(**inputs).last_hidden_state[:, 0, :]  # [1, hidden_size]

    current_dim = embedding.size(1)
    target_dim = 1536

    if current_dim < target_dim:
        # 0으로 채운 패딩 벡터 생성 (2D)
        pad = torch.zeros((1, target_dim - current_dim), device=embedding.device, dtype=embedding.dtype)
        padded_embedding = torch.cat([embedding, pad], dim=1)
    else:
        padded_embedding = embedding[:, :target_dim]

    logger.info("한국어 임베딩 생성 완료")
    return padded_embedding.squeeze(0).tolist()  # [dim] 형태로 반환