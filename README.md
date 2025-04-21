# 🧠 embed-service

> **텍스트 임베딩 생성 API 서비스**  
> 질문/문서 등 다양한 텍스트 입력을 벡터로 임베딩하여 반환하는 FastAPI 기반의 경량 REST API


## ✅ 개요

이 서비스는 `POST /embed/text` API를 통해 입력된 `raw_text`를 벡터 임베딩으로 변환합니다.  
향후 LLM 기반 RAG 시스템의 공통 임베딩 서비스로 활용됩니다.


## 🧩 API 명세

- **Endpoint**: `POST /embed/text`
- **Request**:
```json
{
  "raw_text": "서울시 청년 지원 정책에 대해 알려줘."
}
```
- **Response**:
```json
{
  "embedding_vector": [0.123, 0.456, 0.789, ...]
}
```
- Status Codes:
	- 200 OK: 성공
	- 400 Bad Request: 요청 파라미터 오류
	- 500 Internal Server Error: 서버 내부 오류


## 🚀 로컬 실행 방법
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 서버 실행
uvicorn main:app --reload --port 8000
```

## 🐳 Docker로 빌드 & 실행
```bash
# 빌드
docker build -t embed-service .

# 실행
docker run -p 8000:8000 embed-service
```


## ⚙️ CI/CD (ECR 배포)
GitHub Actions를 활용하여 dev 브랜치에 push 시 AWS ECR로 자동 배포됩니다.

- ECR:
	- Repository: embed-service
	- Tag: Git SHA 또는 latest
> 📦 .github/workflows/deploy.yml 참고


## 🛠️ TODO
- 실제 임베딩 모델 연결 (e.g. Bedrock, HuggingFace, 내부 모델 등)
- 로깅/모니터링 추가 (OpenTelemetry 등)
- 요청/응답 예외 처리 정교화
- 헬스체크 엔드포인트 추가


## 📁 디렉토리 구조

(작성중)