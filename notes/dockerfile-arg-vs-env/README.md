---
title: "Dockerfile ARG vs ENV 차이, FROM 앞 ARG가 스테이지에서 빈 값이 되고 토큰이 docker history에 남은 기록"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3046
---

# Dockerfile ARG·ENV: 재현 출력 원문과 기존 설명 정정 표

ARG·ENV 값이 빌드 중, 이미지, 컨테이너 중 어디에 보이는지를 Mac Docker Desktop 재현 출력과 Docker 공식 문서로 대조한 노트다. 같은 주소에 있던 이전 글과 한국어 상위 글의 설명 중 문서·재현과 어긋나는 부분을 주장별로 정리했다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 정정 표, 재현 환경, 재현 출력 원문(더미 값), 한계 |
| `figure-1-visibility.csv` | 도식 「값이 보이는 구간」 원자료. 수단 4종 × 빌드 중·이미지·컨테이너 |
| `figure-2-arg-scope.csv` | 도식 「FROM 앞 ARG 범위」 원자료. Dockerfile 줄별로 풀린 값 |
| `figures/` | 글에 쓴 도식 원본 |

## 기존 설명 정정 표

판정 기준은 Docker 공식 문서(아래 출처)와 2026-11-16 재현 출력이다. 「이전 글」은 같은 URL에 2025-09-08 올렸던 버전, 「상위 글」은 같은 검색어의 한국어 상위 노출 글이다.

| 기존 주장 | 어디서 | 판정 | 근거 |
|---|---|---|---|
| ARG는 빌드 시에만 쓰이고 `--build-arg`로 넘긴다 | 이전 글 | 맞음 | Build variables |
| ARG는 실행 중 앱 코드에서 읽을 수 없다 | 이전 글 | 맞음 | Build variables. 런타임에 쓰려면 `ENV X=$X`로 옮긴다 |
| ARG는 이미지에 저장되지 않는다 | 이전 글 비교표 | 틀림 | Build variables: build arg·env 값은 이미지 메타데이터, provenance attestation, 이미지 history에 남을 수 있다. 재현: 기본값 없는 `ARG GRADLE_TOKEN`에 `--build-arg`로 넘긴 값이 history에 `ARG GRADLE_TOKEN=<더미 토큰>`으로 찍힘 |
| ENV는 컨테이너 실행 때 쓰인다 | 이전 글 비교표 | 불완전 | ENV는 선언 뒤 빌드 단계 RUN에도 적용되고 컨테이너까지 이어진다 |
| `ENV PORT 80`(공백 구분) | 이전 글 | 구식 표기 | Dockerfile reference: 공백 구분은 하위 호환으로만 지원, `ENV PORT=80` 권장 |
| `ARG DEFAULT_PORT=80` → `ENV PORT=$DEFAULT_PORT` | 이전 글 | 맞음 | Build variables의 `ARG NODE_ENV` → `ENV NODE_ENV=$NODE_ENV` 예시와 같은 패턴 |
| `-e PORT=8000`으로 실행하면 포트가 바뀐다 | 이전 글 | 일부 보강 | 앱은 8000을 읽지만 `EXPOSE $PORT`는 빌드 때 값(80)으로 이미지 메타데이터에 남는다. 실제 공개는 `-p` |
| ENV에 넣은 비밀값은 `docker history`로 보인다 | 이전 글 | 맞음, 범위 확장 | ARG도 같다. 빌드 중 대안은 `RUN --mount=type=secret` |
| ENV 값을 `--build-arg`로 바꿀 수 있다 | 상위 글 | 틀림 | Dockerfile reference: 같은 이름이면 ENV가 ARG를 항상 덮는다 |
| 선언 없는 `--build-arg`는 "were not consumed" 경고가 뜬다 | 여러 글 | 이 환경에서 재현 안 됨 | BuildKit 기본 환경에서 선언 없는 `--build-arg FOO=bar`는 경고 없이 버려졌다 |

## 재현 환경

- 날짜: 2026-11-16
- 기기: Mac
- Docker Desktop 4.96.3, Docker Engine 29.9.2
- `docker buildx` v0.39.0, `docker compose` v5.7.1, BuildKit v0.35.0
- 빌더: BuildKit(Engine 23.0부터 Linux 기본, 별도 설정 없음)

재현에 쓴 Dockerfile·compose 파일 전문은 싣지 않는다. 아래 출력은 재현 때 받은 원문이며, 토큰 자리는 재현용 더미 문자열을 `<더미 토큰>`으로 바꿔 적었다.

## 재현 출력 원문

### 1. FROM 앞 ARG와 스테이지 안 재선언

실행 스테이지 안에서 재선언 전 라벨 `jdk_before`, 재선언 뒤 라벨 `jdk_after`를 두고 빌드했다.

빌드 로그 맨 위:

```
#1 WARN: UndefinedVar: Usage of undefined variable '$JDK_VERSION' (line 3)
```

이미지 config의 라벨:

```
{ "jdk_after": "21", "jdk_before": "" }
```

`docker history` 순서: `LABEL jdk_before=` → `ARG JDK_VERSION=21` → `LABEL jdk_after=21`.

### 2. compose `build.args`와 `environment`에 같은 이름

설명용으로 `JDK_VERSION`을 `build.args`에는 21, `environment`에는 17로 넣고 `docker compose config`를 실행했다. `context` 경로는 가렸다.

```
name: cmp
services:
  app:
    environment:
      JDK_VERSION: "17"
      SPRING_PROFILES_ACTIVE: prod
    build:
      context: <프로젝트 경로>
      dockerfile: Dockerfile
      args:
        JDK_VERSION: "21"
```

### 3. 토큰을 ARG·ENV로 넣은 이미지

Dockerfile에는 기본값 없이 `ARG GRADLE_TOKEN`만 두고, 값은 `--build-arg`로 넘겼다. `docker history --no-trunc`의 해당 줄:

```
ARG GRADLE_TOKEN=<더미 토큰>
ENV NPM_TOKEN=<더미 토큰>
```

같은 Dockerfile에 `docker build --check`:

```
#1 WARN: SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "GRADLE_TOKEN") (line 2)
#1 WARN: SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ENV "NPM_TOKEN") (line 3)
```

### 4. `RUN --mount=type=secret,id=gradle_token`으로 바꾼 뒤

- `docker build --check`: 경고 0줄
- `docker history --no-trunc`: RUN 명령 글자만 남고 토큰 값은 없음
- compose `build.secrets`(최상위 `secrets.gradle_token.environment: NEXUS_TOKEN`)의 `docker compose config`: `environment: NEXUS_TOKEN`까지만 표시, 값 없음

### 5. 선언 없는 `--build-arg`

`ARG FOO` 선언이 없는 Dockerfile에 `--build-arg FOO=bar`를 넘겨 빌드: 경고 없이 빌드 완료, FOO 값은 어디에도 쓰이지 않음.

## 출처

- Docker Docs, Build variables — https://docs.docker.com/build/building/variables/
- Docker Docs, Dockerfile reference (ARG, ENV, EXPOSE) — https://docs.docker.com/reference/dockerfile/
- Docker Docs, SecretsUsedInArgOrEnv — https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/
- Docker Docs, Build secrets — https://docs.docker.com/build/building/secrets/
- Docker Docs, Compose Build Specification — https://docs.docker.com/reference/compose-file/build/

## 한계

- 재현은 Mac 한 대, 위 버전 조합 한 번이다. 다른 Engine·BuildKit 버전에서는 빌드 체크 이름과 경고 문구가 다를 수 있다.
- SecretsUsedInArgOrEnv 경고 문구는 공식 문서에 적힌 메시지("Potentially sensitive data should not be used in the ARG or ENV commands")와 다르다. 위 출력은 이 환경에서 받은 그대로다.
- 이 검사가 어떤 단어를 비밀값 이름으로 보는지 공식 문서에 목록이 없다. 재현에서 걸린 이름은 `GRADLE_TOKEN`·`NPM_TOKEN` 두 개다.
- 선언 없는 `--build-arg` 결과(5번)는 BuildKit 기본 환경에서 확인한 것이다. 구형 빌더에서는 확인하지 않았다.
- 2번 compose 출력은 동작을 보이려고 일부러 같은 이름에 다른 값을 넣은 설정이다.
