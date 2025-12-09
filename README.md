# 🎵 Discord Music Bot

[![CI/CD Pipeline](https://github.com/YOUR_USERNAME/musicbot/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/musicbot/actions/workflows/ci-cd.yml)

Discord 음성 채널에서 YouTube 음악을 재생하는 기능이 풍부한 음악 봇입니다.

## ✨ 주요 기능

### 🎛️ 인터랙티브 대시보드
- 실시간 업데이트되는 음악 제어판
- 버튼 기반 제어 (일시정지, 재생, 스킵)
- 현재 재생 중인 곡 및 다음 3곡 미리보기
- 스레드 기반 활동 로그

### 🔍 노래 검색 및 재생
- **Modal 검색창**: 대시보드에서 "🔍 검색" 버튼으로 팝업 검색
- **커맨드 방식**: `!play <노래 제목>` 또는 `!play <YouTube URL>`
- 자동 YouTube 검색
- URL 직접 재생 지원

### 📋 대기열 관리
- **전체 대기열 보기**: `!queue` 또는 "대기열 보기" 버튼
- **곡 삭제**:
  - 커맨드: `!remove <번호>` (예: `!remove 2`)
  - Select Menu: "대기열 보기" 버튼에서 드롭다운으로 선택 삭제
- 최대 25곡까지 UI에서 관리

### 🎵 재생 제어
- `!play <검색어/URL>` - 노래 검색 및 재생
- `!skip` - 현재 곡 스킵
- `!stop` - 재생 중지
- `!queue` - 대기열 보기
- `!remove <번호>` - 대기열에서 특정 곡 삭제
- `!join` - 음성 채널 참여
- `!leave` - 음성 채널 나가기

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.11+
- Discord Bot Token
- FFmpeg (플랫폼별 설치 필요)

### 1️⃣ 로컬 실행 (개발)

#### Windows
```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/musicbot.git
cd musicbot

# FFmpeg 설치 (최초 1회)
# 방법 1: Chocolatey 사용 (권장)
choco install ffmpeg

# 방법 2: 수동 다운로드
# https://www.gyan.dev/ffmpeg/builds/
# 다운로드 후 PATH에 추가

# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
copy config.example.json config.json
# config.json 편집하여 토큰 입력

# 실행
python musicbot.py
```

#### macOS
```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/musicbot.git
cd musicbot

# FFmpeg 설치
brew install ffmpeg

# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config.example.json config.json
# config.json 편집하여 토큰 입력

# 실행
python musicbot.py
```

#### Linux (Ubuntu/Debian)
```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/musicbot.git
cd musicbot

# FFmpeg 설치
sudo apt update && sudo apt install ffmpeg

# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 설정 파일 생성
cp config.example.json config.json
# config.json 편집하여 토큰 입력

# 실행
python musicbot.py
```

### 2️⃣ Docker 실행 (권장)

#### Docker Compose 사용
```bash
# config.json 생성
cp config.example.json config.json
# config.json 편집하여 토큰 입력

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

#### Docker 직접 실행
```bash
# 프라이빗 레지스트리 로그인
docker login registry.ryein.kim

# 이미지 받기
docker pull registry.ryein.kim/music-bot:latest

# 실행
docker run -d \
  --name musicbot \
  --restart unless-stopped \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/logs:/app/logs \
  registry.ryein.kim/music-bot:latest
```

### 3️⃣ Private Docker Registry에서 이미지 받기

```bash
# 레지스트리 로그인
docker login registry.ryein.kim

# 최신 버전
docker pull registry.ryein.kim/music-bot:latest

# 특정 버전
docker pull registry.ryein.kim/music-bot:v1.0.0

# 특정 브랜치 빌드
docker pull registry.ryein.kim/music-bot:main
```

## 🔧 설정

### config.json
```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "prefix": "!",
  "owner_id": "YOUR_DISCORD_USER_ID"
}
```

### 환경 변수 (Docker)
```bash
# config.json 대신 환경 변수 사용 가능
DISCORD_TOKEN=your_token_here
COMMAND_PREFIX=!
OWNER_ID=your_user_id
```

## 📦 CI/CD 파이프라인

이 프로젝트는 GitHub Actions를 통한 완전 자동화된 CI/CD를 지원합니다.

### 🔐 초기 설정 (필수)

CI/CD를 사용하기 전에 **GitHub Secrets 설정**이 필요합니다:

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 추가:
   - `DOCKER_REGISTRY_USERNAME` - Docker Registry 사용자명
   - `DOCKER_REGISTRY_PASSWORD` - Docker Registry 비밀번호/토큰

**📖 자세한 설정 방법**: [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md) 참고

### CI/CD 파이프라인 구성

### 자동화 작업
1. **코드 품질 검사**
   - Flake8 린트
   - Black 코드 포맷 검사
   - Python 문법 검증

2. **Docker 이미지 빌드**
   - Multi-platform 빌드 (amd64, arm64)
   - GitHub Container Registry에 자동 푸시
   - 태그 자동 생성 (latest, version, sha)

3. **보안 스캔**
   - Trivy 취약점 스캐닝
   - GitHub Security 통합

4. **배포 알림**
   - 빌드 상태 요약
   - Docker 이미지 pull 명령어 제공

### 트리거
- `main` 또는 `develop` 브랜치에 push
- Pull Request 생성
- Version 태그 생성 (`v*`)

## 🏗️ 프로젝트 구조

```
musicbot/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions 워크플로우
├── ffmpeg/                     # FFmpeg 바이너리 (Windows)
│   └── bin/
│       ├── ffmpeg.exe
│       ├── ffplay.exe
│       └── ffprobe.exe
├── .venv/                      # Python 가상환경 (gitignore)
├── logs/                       # 로그 파일 (gitignore)
├── musicbot.py                 # 메인 봇 애플리케이션
├── musicbot_backup.py          # 백업 파일
├── requirements.txt            # Python 의존성
├── config.json                 # 봇 설정 (gitignore)
├── config.example.json         # 설정 템플릿
├── Dockerfile                  # Docker 이미지 빌드
├── docker-compose.yml          # Docker Compose 설정
├── .dockerignore              # Docker 빌드 제외 파일
├── .gitignore                 # Git 제외 파일
└── README.md                   # 프로젝트 문서
```

## 🛠️ 개발

### 개발 환경 설정
```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/musicbot.git
cd musicbot

# 가상환경 생성
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 개발 의존성 설치
pip install -r requirements.txt
pip install black flake8 pytest
```

### 코드 포맷팅
```bash
# Black으로 자동 포맷
black .

# Flake8으로 린트
flake8 musicbot.py
```

### 로컬 Docker 빌드
```bash
# 이미지 빌드
docker build -t musicbot:dev .

# 실행
docker run -it --rm \
  -v $(pwd)/config.json:/app/config.json:ro \
  musicbot:dev
```

## 📚 기술 스택

- **언어**: Python 3.11
- **라이브러리**:
  - `discord.py` - Discord API 래퍼
  - `yt-dlp` - YouTube 콘텐츠 추출
  - `PyNaCl` - 음성 암호화
- **인프라**:
  - Docker / Docker Compose
  - GitHub Actions (CI/CD)
  - GitHub Container Registry (이미지 저장소)
- **오디오**:
  - FFmpeg (인코딩/스트리밍)
  - Opus 코덱

## 🤝 기여

기여를 환영합니다! 다음 절차를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🐛 문제 해결

### FFmpeg를 찾을 수 없음
- **Windows**: `ffmpeg/bin/` 디렉토리에 FFmpeg 바이너리 확인
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### Discord 연결 오류
- config.json의 토큰이 올바른지 확인
- 봇이 서버에 초대되어 있는지 확인
- 봇에 음성 채널 권한이 있는지 확인

### Docker 권한 오류
```bash
# config.json 파일 권한 설정
chmod 644 config.json

# logs 디렉토리 권한 설정
mkdir -p logs
chmod 755 logs
```

## 📧 연락처

문제가 있으시면 [Issues](https://github.com/YOUR_USERNAME/musicbot/issues)에 등록해주세요.

---

**Made with ❤️ and 🎵**
