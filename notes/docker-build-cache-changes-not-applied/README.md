---
title: "Docker 코드 수정 반영 안 될 때 원인 확인 순서, 컨테이너 이미지 ID 앞 12자리부터 본다"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3022
---

# Docker 반영 문제: 옛 글 검증, 캐시 무효화 규칙, compose 재생성 조건

이 노트는 2025-08-08에 같은 주소로 올렸던 옛 글의 주장을 공식 문서로 다시 확인한 결과와, 빌드 캐시가 깨지는 조건·compose 명령별로 컨테이너가 다시 만들어지는 조건을 Docker 공식 문서와 대조한 표를 모은다. 기준일은 2026-11-16이다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 옛 글 검증표, 캐시 무효화 규칙 대조표, compose 명령별 재생성 조건표, 출처, 한계 |
| `figures/` | 글에 쓴 도식 원본(확인 순서 흐름도, WSL2 경로별 결과) |

## 확인 방법

- 각 문서는 2026-11-16에 웹으로 열어 해당 문장을 원문으로 확인했다.
- Compose services 문서의 `pull_policy` 문장은 요약 도구가 내용을 가져오지 못해 헤드리스 브라우저로 렌더링한 원문에서 확인했다.
- 문서 문장을 확인한 것이며, 각 동작을 모든 버전에서 실행해 본 것은 아니다.

## 1. 옛 글(2025-08-08판) 주장 검증

| 옛 글 주장 | 판정 | 비고 |
|---|---|---|
| 빌드 시점에 파일이 이미지에 복사·고정되므로 이후 수정은 기존 이미지에 반영되지 않는다 | 유효 | bind mount를 쓰면 이미지 속 파일이 마운트에 가려진다는 갈래가 빠져 있었다 |
| 이미지는 수정할 수 없는 스냅샷이다 | 유효 | |
| 중간 레이어가 바뀌면 그 뒤 레이어는 모두 다시 실행된다 | 유효 | Build cache 문서: 한 번 무효화되면 이후 명령은 캐시를 쓰지 않는다 |
| `COPY . .`가 `npm install`보다 앞이면 코드만 바꿔도 설치가 매번 다시 돈다 | 유효 | 반영 문제가 아니라 빌드 속도 문제라 새 글에서는 로그 읽는 법으로만 남겼다 |
| `docker build .` 뒤 `docker run <새 이미지 ID>` | 유효하지만 불충분 | 기존 컨테이너를 `start`·`restart`로 켜면 옛 이미지 그대로라는 점, Compose `up`의 재생성 조건이 빠져 있었다 |
| `COPY package.json ./` → `RUN npm install` → `COPY . .` | 보완 | lockfile(`package-lock.json`)을 함께 복사하고 `npm ci`로 설치하도록 고쳤다 |

옛 글에 없던 항목: Compose `up`의 이미지 재사용과 재생성 조건, `restart`와 재생성의 차이, bind mount와 개발 서버 변경 감지, `.dockerignore`·컨텍스트 밖 파일, `RUN` 명령 문자열 캐시, 서버의 `latest` 처리, 이미지 ID로 확인하는 순서.

## 2. 빌드 캐시가 깨지는 조건

| 대상 | 캐시를 다시 쓰는 기준 | 깨지는 경우 | 출처 |
|---|---|---|---|
| `COPY` / `ADD` | 복사할 파일의 내용과 메타데이터로 만든 체크섬 | 파일 내용이 바뀌면. 수정 시각(mtime)만 바뀐 것은 체크섬에 들어가지 않는다 | Build cache invalidation |
| `RUN` | 명령 문자열 | 명령 문자열이 바뀌면. 빌드 사이에 외부 결과(패키지 목록, 원격 저장소, 다운로드 파일)가 바뀐 것은 보지 않는다 | Build cache invalidation |
| `ARG` | 빌드 인자 값 | 값이 바뀌면 그 인자를 쓰는 이후 명령의 캐시가 깨진다. 빌드 때 값을 바꿔 특정 지점부터 다시 돌리는 데 쓴다 | Build cache invalidation |
| 이후 단계 | 앞 단계 캐시 사용 여부 | 한 단계가 무효화되면 그 뒤 단계는 모두 다시 실행된다 | Docker build cache |
| `.dockerignore` | 컨텍스트에 포함된 파일만 전달 | 제외된 파일은 `COPY`·`ADD`·bind mount로 이미지에 넣을 수 없다 | Build context |

| 옵션·명령 | 하는 일 | 하지 않는 일 |
|---|---|---|
| `docker build --no-cache` / `docker compose build --no-cache` | 모든 단계를 캐시 없이 다시 실행 | 이미 받아 둔 베이스 이미지를 새로 받지 않는다. 컨텍스트 안의 옛 파일을 새로 만들지 않는다 |
| `docker build --no-cache-filter <스테이지>` | 지정한 스테이지만 캐시 없이 빌드 | 다른 스테이지의 캐시는 그대로 쓴다 |
| `--pull` | 베이스 이미지를 레지스트리에서 다시 확인해 받는다 | 단계 캐시를 버리지 않는다 |
| `docker builder prune` | 빌드 캐시를 지운다 | 이미 만들어진 컨테이너를 새 이미지로 바꾸지 않는다 |
| `docker compose up --no-cache` | 없는 옵션이다 | `up` 옵션 목록에 `--no-cache`가 없다 |

## 3. Compose 명령별 재생성 조건

| 명령 | 이미지 | 컨테이너 | 출처 문장 요지 |
|---|---|---|---|
| `docker compose restart` / `start` | 바뀌지 않음 | 같은 컨테이너를 다시 켬 | 기존 컨테이너 재시작 |
| `docker compose up -d` | 있는 이미지 사용 | 컨테이너 생성 뒤 서비스 설정이나 이미지가 바뀐 경우에만 멈추고 다시 만듦 | compose up 레퍼런스 |
| `docker compose up -d --build` | 시작 전에 `build:`가 있는 서비스 이미지를 빌드 | 이미지가 바뀌었으면 다시 만듦 | `--build`: Build images before starting containers |
| `docker compose up -d --force-recreate` | 빌드하지 않음 | 설정·이미지가 같아도 다시 만듦 | `--force-recreate` |
| `docker compose up -d -V` (`--renew-anon-volumes`) | — | 이전 컨테이너의 익명 볼륨 데이터를 이어 쓰지 않고 새로 만듦 | `-V` |
| `docker compose pull` | 레지스트리의 새 이미지를 받음 | 다시 만들지 않음. 이후 `up -d`가 필요 | |
| `pull_policy: missing`(기본) | 로컬에 없을 때만 받음. 단 `latest` 태그는 `missing`에서도 항상 받는다고 현행 문서에 적혀 있다 | | Compose services `pull_policy` |

`pull_policy`의 `latest` 문장은 현행 Compose(V2) 문서 기준이다. 글에 적은 서버 사례는 docker-compose v1(1.29대) 시절이며, 두 버전의 동작을 같은 조건에서 비교 실행하지는 않았다.

## 4. 기타 확인 사항

| 항목 | 내용 | 출처 |
|---|---|---|
| 볼륨 초기화 | 비어 있는 볼륨을 파일이 있는 컨테이너 경로에 붙이면 그 파일이 볼륨으로 복사된다. 비어 있지 않은 볼륨은 컨테이너 쪽 파일을 가린다 | Volumes |
| Compose watch | 동작 `sync`·`rebuild`·`sync+restart`. Compose 2.22.0 이상, `sync+restart`는 2.23.0 이상 | Use Compose Watch |
| WSL 파일 위치 | Linux 명령줄에서 작업하는 파일은 WSL의 Linux 파일 시스템(홈 디렉터리 아래)에 두라고 권장. 문서의 이유는 성능이며 파일 변경 감지는 다루지 않는다 | Microsoft Learn |

## 출처

- Docker Docs, Build cache invalidation — https://docs.docker.com/build/cache/invalidation/
- Docker Docs, Docker build cache — https://docs.docker.com/build/cache/
- Docker Docs, Build context — https://docs.docker.com/build/concepts/context/
- Docker Docs, docker compose up — https://docs.docker.com/reference/cli/docker/compose/up/
- Docker Docs, docker compose build — https://docs.docker.com/reference/cli/docker/compose/build/
- Docker Docs, Compose services (pull_policy) — https://docs.docker.com/reference/compose-file/services/#pull_policy
- Docker Docs, Volumes — https://docs.docker.com/engine/storage/volumes/
- Docker Docs, Use Compose Watch — https://docs.docker.com/compose/how-tos/file-watch/
- Microsoft Learn, Working across file systems — https://learn.microsoft.com/en-us/windows/wsl/filesystems

## 한계

- 표의 내용은 2026-11-16 문서 문구 기준이며 이후 바뀔 수 있다. 특히 Compose watch 버전 요건과 `pull_policy` 설명은 시효가 있다.
- `--no-cache-filter`, `--force-recreate`, `docker builder prune`은 문서로 확인한 동작이고 글에서 실행 사례로 다루지 않았다.
- 글의 빌드 로그(`CACHED` / `DONE`)는 최소 Dockerfile로 재현한 것이며 원래 사건의 로그가 아니다.
