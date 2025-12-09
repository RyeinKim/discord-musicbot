# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 FFmpeg 설치
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY v5_2.py .
COPY config.json .

# FFmpeg 바이너리 복사 (Windows용이지만 호환성을 위해)
COPY ffmpeg/ ./ffmpeg/

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 포트 노출 (Discord 봇은 포트를 사용하지 않지만, 필요시 사용)
EXPOSE 8080

# 봇 실행
CMD ["python", "v5_2.py"]

