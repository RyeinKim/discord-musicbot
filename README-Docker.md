# Discord 음악 봇 - Docker 사용법

## 🐳 도커로 봇 실행하기

### 1. 도커 이미지 빌드

```bash
# 현재 디렉토리에서 도커 이미지 빌드
docker build -t discord-music-bot .

# 또는 태그와 함께 빌드
docker build -t discord-music-bot:v1.0 .
```

### 2. 도커 컴포즈로 실행 (권장)

```bash
# 봇 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 봇 중지
docker-compose down
```

### 3. 도커 명령어로 직접 실행

```bash
# 봇 실행
docker run -d --name discord-music-bot discord-music-bot

# 로그 확인
docker logs -f discord-music-bot

# 봇 중지 및 삭제
docker stop discord-music-bot
docker rm discord-music-bot
```

### 4. 우분투에서 도커 허브에서 이미지 가져오기

```bash
# 도커 허브에서 이미지 가져오기 (이미지를 푸시한 후)
docker pull your-username/discord-music-bot:latest

# 이미지 실행
docker run -d --name discord-music-bot your-username/discord-music-bot:latest
```

## 📁 파일 구조

```
musicbot/
├── v5_2.py              # 메인 봇 파일
├── config.json          # 봇 설정 파일
├── requirements.txt     # Python 패키지 목록
├── Dockerfile          # 도커 빌드 설정
├── .dockerignore       # 도커 빌드 제외 파일
├── docker-compose.yml  # 도커 컴포즈 설정
├── ffmpeg/             # FFmpeg 바이너리
└── README-Docker.md    # 이 파일
```

## ⚙️ 설정

### config.json 예시
```json
{
  "token": "your-discord-bot-token",
  "prefix": "!",
  "owner_id": "your-owner-id"
}
```

## 🔧 문제 해결

### 1. FFmpeg 관련 오류
- 도커 이미지에 FFmpeg가 포함되어 있습니다
- 추가 설정이 필요하지 않습니다

### 2. 권한 문제
```bash
# 도커 그룹에 사용자 추가 (우분투)
sudo usermod -aG docker $USER
# 로그아웃 후 다시 로그인
```

### 3. 포트 충돌
- 기본적으로 8080 포트를 사용하지만 Discord 봇은 실제로 포트를 사용하지 않습니다
- 필요시 docker-compose.yml에서 포트 설정을 수정하세요

## 🚀 도커 허브에 이미지 푸시하기

```bash
# 도커 허브에 로그인
docker login

# 이미지에 태그 추가
docker tag discord-music-bot your-username/discord-music-bot:latest

# 이미지 푸시
docker push your-username/discord-music-bot:latest
```

## 📝 로그 확인

```bash
# 실시간 로그 확인
docker-compose logs -f

# 특정 서비스의 로그만 확인
docker-compose logs -f discord-music-bot

# 마지막 100줄 로그 확인
docker-compose logs --tail=100
```

## 🔄 업데이트

```bash
# 이미지 재빌드
docker-compose build --no-cache

# 컨테이너 재시작
docker-compose up -d --force-recreate
```

