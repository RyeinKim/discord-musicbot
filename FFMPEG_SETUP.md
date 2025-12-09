# 🎬 FFmpeg 설치 가이드

Discord Music Bot을 로컬에서 실행하려면 FFmpeg가 필요합니다. Docker를 사용하는 경우 자동으로 설치되므로 이 가이드를 건너뛰어도 됩니다.

## 📋 목차
- [Windows 설치](#windows-설치)
- [macOS 설치](#macos-설치)
- [Linux 설치](#linux-설치)
- [설치 확인](#설치-확인)
- [문제 해결](#문제-해결)

---

## Windows 설치

### 방법 1: Chocolatey 사용 (권장)

가장 간단한 방법입니다.

```powershell
# Chocolatey가 설치되어 있지 않다면:
# https://chocolatey.org/install

# FFmpeg 설치
choco install ffmpeg

# 설치 확인
ffmpeg -version
```

### 방법 2: Scoop 사용

```powershell
# Scoop이 설치되어 있지 않다면:
# https://scoop.sh

# FFmpeg 설치
scoop install ffmpeg

# 설치 확인
ffmpeg -version
```

### 방법 3: 수동 다운로드

1. **FFmpeg 다운로드**
   - 공식 사이트: https://www.gyan.dev/ffmpeg/builds/
   - **ffmpeg-release-essentials.zip** 다운로드 (약 100MB)

2. **압축 해제**
   - 예: `C:\ffmpeg`로 압축 해제

3. **PATH 환경 변수 추가**
   - 시작 메뉴 → "환경 변수" 검색
   - 시스템 환경 변수 편집
   - Path 변수 선택 → 편집
   - 새로 만들기 → `C:\ffmpeg\bin` 추가
   - 확인 클릭

4. **확인**
   ```powershell
   # 새 터미널 열기
   ffmpeg -version
   ```

### 방법 4: 프로젝트 로컬에 설치 (추천)

```powershell
# 프로젝트 디렉토리에서
cd F:\OneDrive\Desktop\Windows\musicbot

# ffmpeg 디렉토리 생성
mkdir ffmpeg\bin

# FFmpeg 다운로드 및 압축 해제
# 1. https://www.gyan.dev/ffmpeg/builds/ 에서 다운로드
# 2. ffmpeg.exe, ffprobe.exe, ffplay.exe와 모든 DLL을
#    musicbot/ffmpeg/bin/ 에 복사

# 봇이 자동으로 로컬 FFmpeg를 감지하여 사용합니다
```

---

## macOS 설치

### Homebrew 사용 (권장)

```bash
# Homebrew가 설치되어 있지 않다면:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# FFmpeg 설치
brew install ffmpeg

# 설치 확인
ffmpeg -version
```

### MacPorts 사용

```bash
# MacPorts가 설치되어 있다면:
sudo port install ffmpeg

# 설치 확인
ffmpeg -version
```

---

## Linux 설치

### Ubuntu / Debian

```bash
# 패키지 목록 업데이트
sudo apt update

# FFmpeg 설치
sudo apt install ffmpeg

# 설치 확인
ffmpeg -version
```

### Fedora / RHEL / CentOS

```bash
# RHEL/CentOS는 EPEL 저장소 활성화 필요
sudo dnf install epel-release  # RHEL/CentOS만

# FFmpeg 설치
sudo dnf install ffmpeg

# 설치 확인
ffmpeg -version
```

### Arch Linux

```bash
# FFmpeg 설치
sudo pacman -S ffmpeg

# 설치 확인
ffmpeg -version
```

---

## 설치 확인

모든 플랫폼에서 다음 명령어로 설치를 확인할 수 있습니다:

```bash
ffmpeg -version
```

**성공적인 출력 예시:**
```
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
built with gcc 11.3.0 (Ubuntu 11.3.0-1ubuntu1~22.04.1)
configuration: ...
```

---

## 문제 해결

### "ffmpeg: command not found" 또는 "ffmpeg을 찾을 수 없음"

**원인**: FFmpeg가 설치되지 않았거나 PATH에 없음

**해결 방법**:

#### Windows
1. 설치 확인: PowerShell에서 `where.exe ffmpeg`
2. PATH 확인: 시스템 환경 변수에 FFmpeg 경로 추가
3. 새 터미널 열기 (기존 터미널은 PATH 갱신 안됨)

#### macOS/Linux
1. 설치 확인: `which ffmpeg`
2. PATH 확인: `echo $PATH`
3. 재설치: 위의 설치 방법 다시 시도

### Discord Bot 실행 시 "FFmpeg를 찾을 수 없습니다" 오류

**해결 방법**:

1. **시스템 FFmpeg 확인**
   ```bash
   ffmpeg -version
   ```

2. **Python에서 확인**
   ```python
   import shutil
   print(shutil.which('ffmpeg'))
   ```

3. **봇 로그 확인**
   ```
   Using FFmpeg executable: /usr/bin/ffmpeg
   ```
   이 메시지가 나오면 정상입니다.

### Windows에서 DLL 오류

**원인**: FFmpeg DLL이 누락됨

**해결 방법**:
1. 전체 FFmpeg 패키지 다운로드 (essentials 버전)
2. 모든 DLL 파일이 ffmpeg.exe와 같은 폴더에 있는지 확인
3. 필요한 DLL:
   - avcodec-XX.dll
   - avformat-XX.dll
   - avutil-XX.dll
   - avfilter-XX.dll
   - swresample-XX.dll
   - swscale-XX.dll

### Docker에서는 작동하는데 로컬에서는 안됨

**원인**: Docker는 FFmpeg가 자동 설치되지만, 로컬은 수동 설치 필요

**해결 방법**:
- 위의 플랫폼별 설치 가이드 따라 FFmpeg 설치

---

## 🐳 Docker 사용 (FFmpeg 설치 불필요)

FFmpeg 설치가 번거롭다면 Docker를 사용하세요:

```bash
# Docker Compose로 실행
docker-compose up -d

# 또는 직접 실행
docker run -d \
  --name musicbot \
  -v $(pwd)/config.json:/app/config.json:ro \
  registry.ryein.kim/music-bot:latest
```

Docker 이미지에는 FFmpeg가 자동으로 포함되어 있습니다.

---

## 📚 추가 자료

- **FFmpeg 공식 사이트**: https://ffmpeg.org/
- **Windows 빌드 다운로드**: https://www.gyan.dev/ffmpeg/builds/
- **FFmpeg 문서**: https://ffmpeg.org/documentation.html

---

**💡 팁**: 대부분의 경우 패키지 매니저(Chocolatey, Homebrew, apt)를 사용하는 것이 가장 간단합니다!
