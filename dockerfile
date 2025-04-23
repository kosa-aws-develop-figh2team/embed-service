FROM python:3.11-slim

# 환경 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 필요한 파일 복사
COPY ./utils /app/utils
COPY ./main.py /app
COPY ./requirements.txt /app

# 의존성 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Hugging Face 모델 미리 다운로드
RUN python -c "\
from transformers import AutoModel, AutoTokenizer; \
AutoModel.from_pretrained('BM-K/KoSimCSE-roberta'); \
AutoTokenizer.from_pretrained('BM-K/KoSimCSE-roberta')"

# 포트 설정
EXPOSE 5001

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]