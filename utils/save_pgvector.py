import psycopg2
from typing import List
import datetime
import logging
import os
import json
import dotenv
dotenv.load_dotenv()

from utils.embedding import get_embeddings

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DB 설정
pg_config = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "dbname": os.getenv("POSTGRES_DB", "yourdb")
}

def count_existing_vectors(service_id: str) -> int:
    """
    주어진 service_id에 대해 이미 저장된 벡터의 개수 반환
    """
    count = 0
    try:
        conn = psycopg2.connect(**pg_config)
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM embeddings WHERE service_id = %s", (service_id,))
            count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        logger.error("기존 벡터 개수 조회 실패", exc_info=True)
    return count

def save_text_to_pg(
    text: str,
    service_id: str,
    conn=None,
    vector_id=None
) -> str:
    """
    단일 텍스트 벡터를 PostgreSQL에 저장
    외부에서 conn을 넘기면 커넥션을 닫지 않음
    """
    if vector_id is None:
        start_id = count_existing_vectors(service_id) # 벡터 개수 == 새로 저장할 청크의 인덱스
        vector_id = f"{service_id}_chunk_{start_id}"
    current_timestamp = datetime.datetime.now(datetime.timezone.utc)
    vector = get_embeddings(text)
    vector_str = json.dumps(vector)

    own_conn = False
    if conn is None:
        conn = psycopg2.connect(**pg_config)
        own_conn = True

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO embeddings (id, service_id, content, embedding, created_at)
                VALUES (%s, %s, %s, %s::vector, %s)
                """,
                (vector_id, service_id, text, vector_str, current_timestamp)
            )
        if own_conn:
            conn.commit()
    except Exception as e:
        if own_conn:
            conn.rollback()
        logger.error("단일 pgvector 저장 실패", exc_info=True)
        raise
    finally:
        if own_conn:
            conn.close()
            logger.info("단일 저장용 PostgreSQL 연결 종료")

    return vector_id


def save_chunks_to_pg(
    chunks: List[str],
    service_id: str,
) -> List:
    """
    여러 텍스트 청크를 PostgreSQL에 일괄 저장
    중간 실패 시 해당 작업만 롤백 및 연결 종료
    
    """
    vector_ids = []
    conn = psycopg2.connect(**pg_config)
    logger.info("PostgreSQL 연결 성공")
    start_id = count_existing_vectors(service_id) # 벡터 개수 == 새로 저장할 청크의 인덱스
    try:
        for n, text in enumerate(chunks[start_id:]):
            vector_id = f"{service_id}_chunk_{start_id+n}"
            saved_id = save_text_to_pg(text, service_id, conn, vector_id)
            vector_ids.append(saved_id)
        conn.commit()
        logger.info(f"총 {len(vector_ids)}개 벡터 저장 성공")
    except Exception as e:
        conn.rollback()
        flag = False
        logger.error("청크 저장 중 오류 발생, 롤백합니다", exc_info=True)
        raise
    finally:
        conn.close()
        flag = True
        logger.info("PostgreSQL 연결 종료")

    return vector_ids, flag