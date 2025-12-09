# 🔐 GitHub Secrets 설정 가이드

CI/CD 파이프라인이 프라이빗 Docker Registry에 접근하려면 GitHub Secrets를 설정해야 합니다.

## 📋 필요한 Secrets

다음 2개의 Secret을 GitHub 저장소에 추가해야 합니다:

1. **`DOCKER_REGISTRY_USERNAME`** - Docker Registry 사용자명
2. **`DOCKER_REGISTRY_PASSWORD`** - Docker Registry 비밀번호 또는 토큰

## 🔧 설정 방법

### 1단계: GitHub 저장소 설정 페이지로 이동

1. GitHub에서 저장소 페이지 열기
2. **Settings** 탭 클릭
3. 왼쪽 사이드바에서 **Secrets and variables** → **Actions** 클릭

### 2단계: Repository Secrets 추가

#### Secret 1: DOCKER_REGISTRY_USERNAME

1. **New repository secret** 버튼 클릭
2. Name: `DOCKER_REGISTRY_USERNAME`
3. Secret: Docker Registry 로그인 사용자명 입력
4. **Add secret** 클릭

#### Secret 2: DOCKER_REGISTRY_PASSWORD

1. **New repository secret** 버튼 클릭
2. Name: `DOCKER_REGISTRY_PASSWORD`
3. Secret: Docker Registry 로그인 비밀번호 또는 토큰 입력
4. **Add secret** 클릭

### 3단계: 설정 확인

설정이 완료되면 다음과 같이 표시됩니다:

```
Repository secrets:
✓ DOCKER_REGISTRY_USERNAME
✓ DOCKER_REGISTRY_PASSWORD
```

## 🚀 테스트

설정 후 코드를 푸시하면 자동으로 CI/CD가 실행됩니다:

```bash
git add .
git commit -m "Test CI/CD with private registry"
git push origin main
```

GitHub Actions 탭에서 워크플로우 실행 상태를 확인할 수 있습니다.

## 🔒 보안 권장사항

### 1. 전용 토큰 사용
- Docker Registry에서 전용 액세스 토큰 생성
- 비밀번호 대신 토큰 사용 권장
- 토큰에 최소 권한만 부여 (읽기/쓰기)

### 2. 토큰 로테이션
- 정기적으로 토큰 갱신 (3~6개월마다)
- 이전 토큰은 즉시 폐기

### 3. 접근 제한
- GitHub Actions에만 필요한 권한 부여
- 불필요한 권한은 제거

### 4. 감사 로그 확인
- Docker Registry 접근 로그 정기 확인
- 비정상적인 접근 즉시 조치

## 📝 Docker Registry 로그인 정보

현재 설정된 프라이빗 레지스트리:
- **Registry URL**: `registry.ryein.kim`
- **Image Name**: `music-bot`
- **Full Image Path**: `registry.ryein.kim/music-bot:latest`

## 🛠️ 로컬에서 테스트

GitHub에 푸시하기 전에 로컬에서 테스트:

```bash
# 레지스트리 로그인
docker login registry.ryein.kim

# 이미지 빌드
docker build -t registry.ryein.kim/music-bot:test .

# 이미지 푸시
docker push registry.ryein.kim/music-bot:test
```

## ❓ 문제 해결

### "Error: Username and password required" 오류

**원인**: GitHub Secrets이 올바르게 설정되지 않음

**해결**:
1. GitHub Settings → Secrets 확인
2. Secret 이름 철자 확인 (대소문자 구분)
3. Secret 값이 비어있지 않은지 확인

### "unauthorized: authentication required" 오류

**원인**: 레지스트리 인증 정보가 잘못됨

**해결**:
1. Docker Registry 로그인 정보 재확인
2. 토큰 유효기간 확인
3. 토큰 권한 확인 (push 권한 필요)

### "denied: requested access to the resource is denied" 오류

**원인**: 레지스트리 접근 권한 부족

**해결**:
1. 사용자 계정에 push 권한이 있는지 확인
2. 레지스트리 관리자에게 권한 요청
3. 토큰에 올바른 권한이 부여되었는지 확인

## 📚 추가 자료

- [GitHub Encrypted Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Docker Registry 인증 문서](https://docs.docker.com/registry/authentication/)
- [GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

---

**🔐 보안 주의사항**: Secret 값은 절대 코드에 하드코딩하거나 로그에 출력하지 마세요!
