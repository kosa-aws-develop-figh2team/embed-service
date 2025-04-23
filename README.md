# 🧠 embed-service
> **텍스트 임베딩 생성 및 검색 API 서비스**  
> 다양한 텍스트를 벡터로 임베딩하고, 이를 PostgreSQL(pgvector)에 저장하거나 검색할 수 있는 FastAPI 기반의 RESTful API 서버입니다.


## ✅ 개요
이 서비스는 다음과 같은 기능을 제공합니다:

1. 단일 텍스트 → 벡터 변환 및 저장
2. 청크 리스트 → 벡터 리스트 생성 및 저장
3. 벡터 기반 유사 문서 검색
4. 저장된 벡터 상태 조회

이 서비스는 LLM 기반 RAG 시스템의 공통 임베딩 및 검색 역할을 수행합니다.


## 🧩 API 명세

### 1. 단일 텍스트 임베딩 저장
- **Endpoint**: `POST /embed/text`
- **Request**:
```json
{
  "raw_text": "서울시 청년 지원 정책에 대해 알려줘.",
  "service_id": "svc-20240421-001"
}
```
- **Response**:
```json
{
  "vector_id": "svc-20240421-001-chuck-0"
}
```

### 2. 청크 리스트 임베딩 저장
- **Endpoint**: `POST /embed/chunks`
- **Request**:
```json
{
  "chunk_list": ["청년 정책은...", "다양한 방식으로..."],
  "service_id": "svc-20240421-001"
}
```
- **Response**:
```json
{
  "vector_ids": ["svc-20240421-001-chuck-0", "svc-20240421-001-chuck-1"]
}
```

### 3. 유사 문서 검색
- **Endpoint**: `POST /embed/retrieve`
- **Request**:
```json
{
  "text": "지금 시행 중인 청년 정책 알려줘.",
  "top_k": 5
}
```
- **Response**:
```json
{
  "results": [
    {"id": "svc-xxx-chunk-10", "service_id": "svc-xxx", "content": "청년 정책은..."},
    ...
  ]
}
```

### 🔹 4. 벡터 저장 여부 조회
- **Endpoint**: `GET /embed/status?service_id=svc-20240421-001`
- **Response**:
```json
{
  "vector_ids": ["svc-20240421-001_chunk_0", "svc-20240421-001_chunk_1"],
  "content": ["청년 정책은...", "다양한 방식으로..."]
}
```

---

## 🚀 로컬 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
uvicorn main:app --reload --port 5001
```

## 🐳 Docker로 빌드 & 실행

```bash
# 빌드
docker build -t embed-service .

# 실행
docker run --env-file .env -p 5001:5001 embed-service
```


## 📦 .env 예시

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=yourdb
```


## 📁 디렉토리 구조

```
.
├── README.md
├── dockerfile
├── main.py
├── requirements.txt
└── utils
    ├── embedding.py
    ├── retriever.py
    └── save_pgvector.py
```


## ⚙️ TODO
- embedding API 리팩토링 및 예외 처리 개선
- tracing 및 metrics 연동 (OpenTelemetry)