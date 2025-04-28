from typing import List, Dict
import psycopg2
import logging
from contextlib import contextmanager
from typing import Generator, Dict
import dotenv
import os
dotenv.load_dotenv()

from utils.embedding import get_embeddings

# 로깅 설정
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# DB 설정
def get_pg_config():
    pg_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "dbname": os.getenv("POSTGRES_DB", "yourdb")
    }
    return pg_config

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_pg_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    PostgreSQL 연결을 생성하는 context manager.
    사용이 끝나면 자동으로 연결 종료됨.
    """
    conn = None
    try:
        logger.info("PostgreSQL 연결 시도 중...")
        pg_config = get_pg_config()
        conn = psycopg2.connect(**pg_config)
        logger.info("PostgreSQL 연결 성공")
        yield conn
    except Exception as e:
        logger.error(f"PostgreSQL 연결 실패: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("PostgreSQL 연결 종료")

def _search_similar_documents(
    text: str,
    top_k: int = 5,
) -> List[Dict]:
    """
    pgvector를 이용해 가장 유사한 문서 청크를 top-k개 검색하여 반환
    """
    results = []
    embedding_vector = get_embeddings(text)
    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT id, service_id, content, embedding <=> %s::vector AS distance
                FROM embeddings
                ORDER BY distance
                LIMIT %s;
            """
            cur.execute(query, (embedding_vector, top_k))
            rows = cur.fetchall()

            for row in rows:
                result = {
                    "id": row[0],
                    "service_id": row[1],
                    "content": row[2],
                }
                results.append(result)

    return results

def search_similar_documents(
    text: str,
    top_k: int = 5,
) -> List[Dict]:
    """
    pgvector와 BM25 키워드 검색을 혼합한 Hybrid Search를 통해
    가장 유사한 문서 청크를 top-k개 검색하여 반환
    """
    results = []
    embedding_vector = get_embeddings(text)
    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT id, service_id, content,
                       (0.5 * (1 - (embedding <=> %s::vector)) + 0.5 * ts_rank_cd(to_tsvector('simple', content), plainto_tsquery('simple', %s))) AS hybrid_score
                FROM embeddings
                ORDER BY hybrid_score DESC
                LIMIT %s;
            """
            cur.execute(query, (embedding_vector, text, top_k))
            rows = cur.fetchall()

            for row in rows:
                result = {
                    "id": row[0],
                    "service_id": row[1],
                    "content": row[2],
                }
                results.append(result)

    return results

def get_embedding_status(service_id: str) -> Dict:
    query = """
        SELECT id, content
        FROM embeddings
        WHERE service_id = %s;
    """
    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (service_id,))
            rows = cur.fetchall()
            return {
                "vector_ids": [row[0] for row in rows],
                "content": [row[1] for row in rows]
            }