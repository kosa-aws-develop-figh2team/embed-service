# Dockerfile
FROM python:3.11-slim

# 환경 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY ./embedding.py /app
COPY ./main.py /app
COPY ./requirements.txt /app

# 의존성 설치
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 포트 설정
EXPOSE 5001

# FastAPI 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]