---
title: "맥북 도커 설치, Mac Docker Desktop을 brew로 깔고 hello-world까지 7분, 그 뒤 막힌 에러 3개"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3007
---

# Docker Desktop Mac 설치 — 조회 원자료

글에 나온 설치 파일 크기, Homebrew cask 정보, 이미지별 플랫폼 조회 결과의 원값과 조회 방법을 모았다. 글에서 줄인 공식 기본값 변화와 여러 대 배포용 CLI 설치 절차도 여기에 둔다.

## 파일

| 파일 | 내용 |
|---|---|
| `platforms.csv` | Docker Hub 이미지 5개 태그의 플랫폼 조회 결과(2026-11-16) |
| `platforms.sh` | 위 조회에 쓴 스크립트. 익명 pull 토큰을 받아 manifest list를 읽는다. 토큰은 변수로만 쓰고 출력하지 않는다 |
| `dmg-content-length.csv` | 칩별 Docker.dmg의 `content-length` 원값 |
| `brew-cask-docker-desktop.csv` | Homebrew API의 `docker-desktop` cask 필드 발췌 |
| `figure-2-memory-cap.csv` | 램별 메모리 상한 막대그래프의 원수치 |
| `figures/` | 글에 쓴 도식·터미널·공개 페이지 캡처 PNG |

## 수집 방법과 기준일

모두 2026-11-16에 Linux PC에서 조회했다. Docker Engine은 쓰지 않았고 HTTP 요청만 보냈다.

- **플랫폼 조회**: `sh platforms.sh library/mysql 5.7`처럼 저장소와 태그를 넘긴다. `auth.docker.io`에서 pull 범위 토큰을 받고, `registry-1.docker.io/v2/<저장소>/manifests/<태그>`를 OCI index·Docker manifest list 형식으로 요청한다. `unknown/unknown` 항목(빌드 증명 attestation)은 플랫폼이 아니라서 걸렀다.
- **dmg 크기**: 공식 다운로드 주소에 `curl -sI`로 헤더만 요청해 `content-length`를 읽었다. 파일은 내려받지 않았다.

  ```sh
  for a in arm64 amd64; do
    printf '%-6s ' "$a"
    curl -sI "https://desktop.docker.com/mac/main/$a/Docker.dmg" | grep -i '^content-length'
  done
  ```

- **brew cask**: `https://formulae.brew.sh/api/cask/docker-desktop.json`에서 `token`, `version`, `old_tokens`, `depends_on` 네 필드만 뽑았다.

  ```sh
  curl -s https://formulae.brew.sh/api/cask/docker-desktop.json \
    | python3 -c 'import sys,json; d=json.load(sys.stdin); [print(f"{k}: {d.get(k)}") for k in ("token","version","old_tokens","depends_on")]'
  ```

## 공식 기본값 변화 대조

예전 설치 글의 화면과 지금 화면이 다른 이유를 버전별로 정리했다.

| 버전 | 바뀐 것 | 출처 |
|---|---|---|
| 4.25 | Rosetta for Linux(Apple silicon에서 x86_64/amd64 컨테이너 에뮬레이션)가 정식 기능이 됐다. Settings > General의 체크박스이고 Apple Virtualization framework에서만 쓸 수 있다 | Docker 블로그 4.25, Docker Desktop settings 문서 |
| 4.35.0 | Apple silicon Mac에서 Docker VMM 베타를 고를 수 있게 됐다 | Docker Desktop release notes |
| 4.44.0 | Apple Virtualization이 기본 VMM이 되고 QEMU 가상화는 빠졌다(4.37.0에서 중단 예고) | Docker Desktop release notes |
| 4.88.0 이하 | 설치 중에 「Use recommended settings / Use advanced settings」 선택 화면이 나왔다. 이후 버전은 이 선택을 설치 뒤 Settings로 옮겼다 | Install Docker Desktop on Mac |
| 4.98.0 | `com.docker.vmnetd` 권한 헬퍼가 빠졌다 | Docker Desktop release notes |
| 현재(2026-11-16) | 신규 설치 기본값은 관리자 권한이 필요 없는 구성이다. CLI는 `$HOME/.docker/bin`에 두고 PATH에 추가하며, `/var/run/docker.sock`은 만들지 않는다(Settings > Advanced에서 허용) | Install Docker Desktop on Mac, Docker Desktop settings |

## 여러 대에 배포할 때의 CLI 설치

공식 문서에 있는 명령줄 설치 절차다. 맥북 한 대에 까는 경우에는 dmg를 드래그하거나 brew를 쓰는 편이 간단하다.

```sh
sudo hdiutil attach Docker.dmg
sudo /Volumes/Docker/Docker.app/Contents/MacOS/install
sudo hdiutil detach /Volumes/Docker
```

## 출처

- Docker Docs, Install Docker Desktop on Mac — https://docs.docker.com/desktop/setup/install/mac-install/
- Docker Docs, Docker Desktop release notes — https://docs.docker.com/desktop/release-notes/
- Docker Docs, Docker Desktop settings — https://docs.docker.com/desktop/settings-and-maintenance/settings/
- Docker Docs, Virtual Machine Manager for Docker Desktop on Mac — https://docs.docker.com/desktop/vmm
- Docker Blog, Docker Desktop 4.25 — https://www.docker.com/blog/docker-desktop-4-25/
- Homebrew Formulae, docker-desktop cask — https://formulae.brew.sh/cask/docker-desktop
- Docker Hub Registry API — https://registry-1.docker.io/v2/

## 한계

- 조회 값은 2026-11-16 한 시점의 것이다. 태그가 가리키는 이미지와 dmg는 새 릴리스가 나오면 바뀐다.
- `figure-2-memory-cap.csv`의 상한은 필자의 권장값이다. 8GB 행은 8GB Windows 노트북 경험에서 나온 판단이고, 8GB Mac에서 잰 값이 아니다. 남는 몫은 램에서 상한을 뺀 계산값이다.
- dmg 다운로드 주소는 공식 설치 문서 버튼이 가리키는 주소를 썼다. 문서의 버튼 주소에는 추적용 쿼리가 붙을 수 있다.
