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
- FFmpeg (플랫폼별 설치 필요 - **[설치 가이드 보기](#-ffmpeg-설치-가이드)**)

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

**방법 1: 환경 변수 사용 (권장)**
```bash
# docker-compose.yml 편집하여 환경 변수 설정
# environment 섹션의 주석을 해제하고 토큰 입력:
#   - DISCORD_TOKEN=your_bot_token_here
#   - COMMAND_PREFIX=!
#   - OWNER_ID=your_discord_user_id

# 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

**방법 2: config.json 파일 사용**
```bash
# config.json 생성
cp config.example.json config.json
# config.json 편집하여 토큰 입력

# 실행
docker-compose up -d
```

#### Docker 직접 실행

**방법 1: 환경 변수 사용 (권장)**
```bash
# 프라이빗 레지스트리 로그인
docker login registry.ryein.kim

# 이미지 받기
docker pull registry.ryein.kim/music-bot:latest

# 환경 변수로 실행
docker run -d \
  --name musicbot \
  --restart unless-stopped \
  -e DISCORD_TOKEN=your_bot_token_here \
  -e COMMAND_PREFIX=! \
  -e OWNER_ID=your_discord_user_id \
  -v $(pwd)/logs:/app/logs \
  registry.ryein.kim/music-bot:latest
```

**방법 2: config.json 파일 마운트**
```bash
# config.json 생성
cp config.example.json config.json
# config.json 편집하여 토큰 입력

# config.json 마운트하여 실행
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

봇은 두 가지 방식으로 설정할 수 있습니다:

### 방법 1: 환경 변수 (권장)

**우선순위가 가장 높으며, Docker 환경에서 권장되는 방식입니다.**

```bash
# 필수 환경 변수
DISCORD_TOKEN=your_discord_bot_token_here

# 선택 환경 변수
COMMAND_PREFIX=!                    # 기본값: !
OWNER_ID=your_discord_user_id      # 선택 사항
```

**Docker 사용 시:**
```bash
docker run -d \
  -e DISCORD_TOKEN=your_token \
  -e COMMAND_PREFIX=! \
  -e OWNER_ID=your_user_id \
  registry.ryein.kim/music-bot:latest
```

### 방법 2: config.json 파일

**로컬 개발 환경에서 사용하기 편리한 방식입니다.**

```json
{
  "token": "YOUR_DISCORD_BOT_TOKEN",
  "prefix": "!",
  "owner_id": "YOUR_DISCORD_USER_ID"
}
```

**설정 우선순위:**
1. 환경 변수 (DISCORD_TOKEN, COMMAND_PREFIX, OWNER_ID)
2. config.json 파일
3. 둘 다 없으면 에러 발생

**보안 권장사항:**
- 환경 변수 사용 시: 토큰이 코드에 포함되지 않아 더 안전
- config.json 사용 시: 반드시 `.gitignore`에 포함되어 있는지 확인

## 📦 CI/CD 파이프라인

이 프로젝트는 GitHub Actions를 통한 완전 자동화된 CI/CD를 지원합니다.

### 🔐 초기 설정 (필수)

CI/CD를 사용하기 전에 **GitHub Secrets 설정**이 필요합니다:

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 추가:
   - `DOCKER_REGISTRY_USERNAME` - Docker Registry 사용자명
   - `DOCKER_REGISTRY_PASSWORD` - Docker Registry 비밀번호/토큰

**📖 자세한 설정 방법**: [GitHub Secrets 설정 가이드](#-github-secrets-설정-가이드) 참고

### CI/CD 파이프라인 구성

**간소화된 2단계 파이프라인:**

1. **코드 품질 검사 (Code Quality & Tests)**
   - Flake8 린트
   - Black 코드 포맷 검사
   - Python 문법 검증

2. **Docker 이미지 빌드 및 푸시 (Build & Push)**
   - Multi-platform 빌드 (linux/amd64, linux/arm64)
   - Private Docker Registry에 자동 푸시 (registry.ryein.kim)
   - 태그 자동 생성 (latest, version, sha, branch)

**빌드된 이미지 특징:**
- ✅ 범용 이미지 (토큰 없음)
- ✅ FFmpeg 자동 설치 (apt-get)
- ✅ 런타임에 환경 변수로 설정 주입

### 트리거
- `main` 또는 `develop` 브랜치에 push
- Pull Request 생성
- Version 태그 생성 (`v*`)

### 배포 방법

빌드된 이미지는 **설정 정보가 포함되지 않은 범용 이미지**입니다.

**실행 시 환경 변수로 설정:**
```bash
docker pull registry.ryein.kim/music-bot:latest
docker run -d \
  -e DISCORD_TOKEN=your_token \
  -e COMMAND_PREFIX=! \
  registry.ryein.kim/music-bot:latest
```

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

## 🎬 FFmpeg 설치 가이드

Discord Music Bot을 로컬에서 실행하려면 FFmpeg가 필요합니다. **Docker를 사용하는 경우 자동으로 설치되므로 이 섹션을 건너뛰어도 됩니다.**

### Windows 설치

#### 방법 1: Chocolatey 사용 (권장)
```powershell
# Chocolatey가 설치되어 있지 않다면: https://chocolatey.org/install
choco install ffmpeg

# 설치 확인
ffmpeg -version
```

#### 방법 2: Scoop 사용
```powershell
# Scoop이 설치되어 있지 않다면: https://scoop.sh
scoop install ffmpeg

# 설치 확인
ffmpeg -version
```

#### 방법 3: 수동 다운로드
1. **FFmpeg 다운로드**: https://www.gyan.dev/ffmpeg/builds/
   - **ffmpeg-release-essentials.zip** 다운로드 (~100MB)
2. **압축 해제**: `C:\ffmpeg`로 압축 해제
3. **PATH 환경 변수 추가**:
   - 시작 메뉴 → "환경 변수" 검색
   - Path 변수 선택 → 편집 → `C:\ffmpeg\bin` 추가
4. **확인**: 새 터미널에서 `ffmpeg -version`

### macOS 설치

```bash
# Homebrew 사용 (권장)
brew install ffmpeg

# 설치 확인
ffmpeg -version
```

### Linux 설치

#### Ubuntu / Debian
```bash
sudo apt update
sudo apt install ffmpeg

# 설치 확인
ffmpeg -version
```

#### Fedora / RHEL / CentOS
```bash
# RHEL/CentOS는 EPEL 저장소 활성화 필요
sudo dnf install epel-release  # RHEL/CentOS만

# FFmpeg 설치
sudo dnf install ffmpeg

# 설치 확인
ffmpeg -version
```

#### Arch Linux
```bash
sudo pacman -S ffmpeg

# 설치 확인
ffmpeg -version
```

---

## 🔐 GitHub Secrets 설정 가이드

CI/CD 파이프라인이 프라이빗 Docker Registry에 접근하려면 GitHub Secrets를 설정해야 합니다.

### 필요한 Secrets

1. **`DOCKER_REGISTRY_USERNAME`** - Docker Registry 사용자명
2. **`DOCKER_REGISTRY_PASSWORD`** - Docker Registry 비밀번호 또는 토큰

### 설정 방법

**1단계: GitHub 저장소 설정 페이지로 이동**
1. GitHub에서 저장소 페이지 열기
2. **Settings** 탭 클릭
3. 왼쪽 사이드바에서 **Secrets and variables** → **Actions** 클릭

**2단계: Repository Secrets 추가**

*Secret 1: DOCKER_REGISTRY_USERNAME*
1. **New repository secret** 버튼 클릭
2. Name: `DOCKER_REGISTRY_USERNAME`
3. Secret: Docker Registry 로그인 사용자명 입력
4. **Add secret** 클릭

*Secret 2: DOCKER_REGISTRY_PASSWORD*
1. **New repository secret** 버튼 클릭
2. Name: `DOCKER_REGISTRY_PASSWORD`
3. Secret: Docker Registry 로그인 비밀번호 또는 토큰 입력
4. **Add secret** 클릭

**3단계: 설정 확인**

설정이 완료되면 다음과 같이 표시됩니다:
```
Repository secrets:
✓ DOCKER_REGISTRY_USERNAME
✓ DOCKER_REGISTRY_PASSWORD
```

### 테스트

설정 후 코드를 푸시하면 자동으로 CI/CD가 실행됩니다:
```bash
git add .
git commit -m "Test CI/CD with private registry"
git push origin main
```

GitHub Actions 탭에서 워크플로우 실행 상태를 확인할 수 있습니다.

### 보안 권장사항

1. **전용 토큰 사용**: 비밀번호 대신 Docker Registry 전용 액세스 토큰 생성
2. **토큰 로테이션**: 정기적으로 토큰 갱신 (3~6개월마다)
3. **접근 제한**: GitHub Actions에만 필요한 최소 권한 부여
4. **감사 로그 확인**: Docker Registry 접근 로그 정기 확인

**🔐 보안 주의사항**: Secret 값은 절대 코드에 하드코딩하거나 로그에 출력하지 마세요!

---

## 🐛 문제 해결

### FFmpeg 관련 오류

#### "ffmpeg: command not found" 또는 "ffmpeg을 찾을 수 없음"

**Windows:**
```powershell
# FFmpeg 경로 확인
where.exe ffmpeg

# 없으면 위의 FFmpeg 설치 가이드 참고
```

**macOS/Linux:**
```bash
# FFmpeg 경로 확인
which ffmpeg

# 없으면 위의 FFmpeg 설치 가이드 참고
```

#### Discord Bot 실행 시 "FFmpeg를 찾을 수 없습니다" 오류

1. **시스템 FFmpeg 확인**: `ffmpeg -version`
2. **Python에서 확인**:
   ```python
   import shutil
   print(shutil.which('ffmpeg'))
   ```
3. **봇 로그 확인**: "Using FFmpeg executable: /usr/bin/ffmpeg" 메시지 확인

#### Windows에서 DLL 오류

**원인**: FFmpeg DLL이 누락됨

**해결**:
1. 전체 FFmpeg 패키지 다운로드 (essentials 버전)
2. 모든 DLL 파일이 ffmpeg.exe와 같은 폴더에 있는지 확인

### Discord 연결 오류

- config.json의 토큰이 올바른지 확인
- 봇이 서버에 초대되어 있는지 확인
- 봇에 음성 채널 권한이 있는지 확인
- 환경 변수 사용 시 `DISCORD_TOKEN`이 올바르게 설정되었는지 확인

### Docker 관련 오류

#### Docker 권한 오류
```bash
# config.json 파일 권한 설정
chmod 644 config.json

# logs 디렉토리 권한 설정
mkdir -p logs
chmod 755 logs
```

#### "Configuration not found" 오류

Docker 실행 시 환경 변수나 config.json이 제공되지 않은 경우:
```bash
# 환경 변수 사용
docker run -d -e DISCORD_TOKEN=your_token registry.ryein.kim/music-bot:latest

# 또는 config.json 마운트
docker run -d -v $(pwd)/config.json:/app/config.json:ro registry.ryein.kim/music-bot:latest
```

### GitHub Actions CI/CD 오류

#### "Username and password required" 오류

**원인**: GitHub Secrets이 올바르게 설정되지 않음

**해결**:
1. GitHub Settings → Secrets 확인
2. Secret 이름 철자 확인 (대소문자 구분)
3. Secret 값이 비어있지 않은지 확인

#### "unauthorized: authentication required" 오류

**원인**: 레지스트리 인증 정보가 잘못됨

**해결**:
1. Docker Registry 로그인 정보 재확인
2. 토큰 유효기간 확인
3. 토큰 권한 확인 (push 권한 필요)

## 📧 연락처

문제가 있으시면 [Issues](https://github.com/YOUR_USERNAME/musicbot/issues)에 등록해주세요.

---

**Made with ❤️ and 🎵**
