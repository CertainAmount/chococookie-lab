---
title: "docker compose up -d 다음 ps -a부터: localhost·healthcheck·포트 충돌, 안 뜨는 원인 3가지"
checked: 2026-11-15
article_url: https://jjeongil.tistory.com/3063
---

# docker compose up -d 재현 노트

글에서 다룬 네 장면(DB 주소 localhost, healthcheck 없는 depends_on, 호스트 5432 점유, down과 down -v)을 다시 만들 때 쓰는 compose 파일과 시나리오별 변경점·명령을 모았다. 글의 공식 동작 설명이 어느 문서에 근거하는지도 함께 대조했다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 재현용 compose 전문, 시나리오별 명령, 공식 레퍼런스 대조, 이미지 태그 확인 기록 |
| `port-5432-lsof-demo.txt` | 리눅스에서 파이썬으로 5432를 점유한 뒤 `lsof`와 두 번째 bind를 실행한 원출력 |
| `figure-3-healthcheck.csv` | 기동 비교 그림(figure-3)에 쓴 healthcheck 설정값과 첫 기동 관찰값 |
| `figures/` | 글에 쓴 도식·터미널 캡처 원본(업로드 스크립트가 채운다) |

## 환경과 기준일

- 장면 재현: macOS, Docker Desktop, Spring Boot(Hikari·Flyway) 백엔드 + PostgreSQL·Redis·Mailpit
- 포트 점유 재현: Docker가 없는 리눅스, Python 3 표준 라이브러리만 사용
- 이미지 태그·공식 문서 확인일: 2026-11-15

## 재현용 compose 전문

비밀번호는 `${POSTGRES_PASSWORD}`로 치환한다. 값은 같은 디렉터리의 `.env`에 두고 저장소에는 `.env.example`만 올린다.

```yaml
services:
  db:
    image: postgres:18.6
    environment:
      POSTGRES_USER: app
      POSTGRES_DB: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "127.0.0.1:5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s

  redis:
    image: redis:8.10-alpine

  mailpit:
    image: axllent/mailpit:v1.27
    ports:
      - "127.0.0.1:8025:8025"

  backend:
    build: ./backend
    environment:
      SPRING_DATASOURCE_URL: jdbc:postgresql://db:5432/app
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

`.env.example`

```
POSTGRES_PASSWORD=
```

- `./backend/Dockerfile`은 멀티스테이지 구성이다. 빌드 단계에서 Gradle `bootJar`를 만들고, 실행 단계는 JRE 이미지에 jar만 복사한다.
- mailpit SMTP(1025)는 호스트에 열지 않는다. 백엔드는 `mailpit:1025`로 접속한다.
- redis는 `ports`가 없다. 호스트에서 확인할 때는 `docker compose exec redis redis-cli`.
- postgres 17로 재현하려면 태그와 함께 마운트 경로를 `pgdata:/var/lib/postgresql/data`로 바꾼다(아래 「postgres 17/18 데이터 경로」).

## 시나리오별 변경점과 명령

각 시나리오가 끝나면 위 전문으로 되돌린다.

### 1. DB 주소를 localhost로

변경: `backend.environment.SPRING_DATASOURCE_URL`을 `jdbc:postgresql://localhost:5432/app`으로. `application.yml`은 바꾸지 않는다(OS 환경변수가 설정 파일보다 우선하므로 compose 값이 이긴다).

```sh
docker compose up -d
docker compose ps -a
docker compose logs --tail 50 backend
```

확인할 것: db는 `(healthy)`, backend는 `Exited (1)`. 로그에 `HikariPool-1 - Exception during pool initialization`과 `Connection to localhost:5432 refused`. `restart: on-failure`를 추가하면 backend 상태가 `Restarting (1)`로 바뀐다.

### 2. healthcheck 없이 depends_on만

변경: db의 `healthcheck` 블록을 지우고, backend의 `depends_on`을 `- db` 목록 형태로 바꾼다.

```sh
docker compose down -v      # 빈 볼륨에서 첫 기동을 만들기 위해. 데이터가 지워진다
docker compose up -d
docker compose ps -a
docker compose logs --tail 50 backend
```

확인할 것: 빈 볼륨 첫 기동에서 initdb가 끝나기 전에 backend가 붙으려다 `db:5432 refused`로 종료. 볼륨이 있는 상태에서 반복하면 가끔 `FATAL: the database system is starting up`.

원상복구 뒤 `docker compose up -d` 출력에서 `Container …-db-1 Waiting` → `Healthy` → `Container …-backend-1 Started` 순서를 확인한다.

### 3. 호스트 5432 점유

변경: db의 `ports`를 `"5432:5432"`로. 호스트에 PostgreSQL이 5432로 떠 있는 상태에서 실행한다.

```sh
docker compose up -d        # Ports are not available ... address already in use
docker ps                   # 다른 컨테이너가 5432를 쥐었는지 먼저
lsof -nP -iTCP:5432 -sTCP:LISTEN
```

`lsof` COMMAND 값: 호스트 설치 PostgreSQL이면 `postgres`, Docker Desktop(Mac)이 연 다른 컨테이너 포트면 `com.docker.backend`.

### 4. down과 down -v

```sh
docker compose exec db psql -U app -d app -c 'select count(*) from orders'
docker compose down
docker volume ls            # {디렉터리이름}_pgdata 남음
docker compose up -d
docker compose exec db psql -U app -d app -c 'select count(*) from orders'
docker compose down -v      # Volume {디렉터리이름}_pgdata Removed
docker volume ls            # 사라짐
docker compose up -d
docker compose exec db psql -U app -d app -c 'select count(*) from orders'
```

결과: 3 → 3 → 0. 마지막이 0인 것은 Flyway가 빈 DB에 스키마를 다시 만들었기 때문이다.

## 포트 점유 재현 (Docker 없이)

```sh
# 터미널 1: 5432를 잡고 기다린다
python3 -c "import socket,time; s=socket.socket(); s.bind(('127.0.0.1',5432)); s.listen(); time.sleep(600)"

# 터미널 2
lsof -nP -iTCP:5432 -sTCP:LISTEN
python3 -c "import socket; socket.socket().bind(('127.0.0.1', 5432))"
```

원출력은 `port-5432-lsof-demo.txt`에 있다. `lsof`는 사용자 이름 등 일부 열을 지운 출력이다. COMMAND `python3`, NAME `127.0.0.1:5432 (LISTEN)`, 두 번째 bind는 `OSError: [Errno 98] Address already in use`.

## 공식 레퍼런스 대조

### depends_on condition

| 값 | 기다리는 것 |
|---|---|
| `service_started` | 의존 서비스 컨테이너 시작(기본 동작과 같음) |
| `service_healthy` | 의존 서비스 healthcheck 통과 |
| `service_completed_successfully` | 의존 서비스가 성공(종료 코드 0)으로 끝남 |

출처: Compose services 레퍼런스, Control startup and shutdown order.

### docker compose down이 지우는 것

| 대상 | `down` | `down -v` |
|---|---|---|
| 컨테이너 | 삭제 | 삭제 |
| compose가 만든 네트워크 | 삭제 | 삭제 |
| named volume | 남음 | 삭제 |
| 익명 볼륨 | 남음(다음 `up`에 다시 붙지 않음) | 삭제 |
| `external: true` 볼륨·네트워크 | 남음 | 남음 |

출처: docker compose down 레퍼런스.

### docker compose up 옵션

| 옵션 | 동작 |
|---|---|
| `-d`, `--detach` | 백그라운드로 실행하고 바로 돌아옴 |
| `--build` | 컨테이너 시작 전에 이미지 빌드 |
| `--wait` | 서비스가 running/healthy가 될 때까지 대기, detach를 함의 |
| `--no-deps` | 연결된 서비스는 시작하지 않음 |
| `--force-recreate` | 설정·이미지가 같아도 컨테이너를 새로 만듦 |

출처: docker compose up 레퍼런스.

### 그 밖의 대조

| 항목 | 근거 |
|---|---|
| `ps -a`가 없으면 종료된 컨테이너가 안 보인다 | docker compose ps 레퍼런스 |
| 최상위 `version` 키는 무시된다(obsolete 경고) | Compose 파일 version and name |
| `.env`는 compose 파일의 `${…}` 치환용, 컨테이너로 넘기려면 `environment`나 `env_file`에 다시 적는다 | Compose 변수 치환 문서 |
| 프로젝트마다 기본 네트워크, 서비스 이름이 호스트명 | Networking in Compose |
| OS 환경변수가 `application.yml`보다 우선 | Spring Boot Externalized Configuration(PropertySource 순서) |
| `pg_isready`는 틀린 사용자·DB로도 상태를 돌려주고, 서버에는 접속 실패가 기록된다 | PostgreSQL pg_isready 문서 Notes |

`pg_isready`에서 `-U`를 빼면 기본 사용자 이름(libpq 기본값, OS 사용자명)으로 접속한다. 컨테이너 안에서는 root라서 db 로그에 `FATAL: role "root" does not exist`가 healthcheck 간격마다 남는다.

## postgres 17/18 데이터 경로

Docker Hub postgres 문서 PGDATA 항목 기준(2026-11-15 확인).

| 메이저 | 이미지가 선언한 VOLUME | PGDATA | named volume 마운트 |
|---|---|---|---|
| 18 이상 | `/var/lib/postgresql` | `/var/lib/postgresql/18/docker` | `pgdata:/var/lib/postgresql` |
| 17 이하 | `/var/lib/postgresql/data` | `/var/lib/postgresql/data` | `pgdata:/var/lib/postgresql/data` |

17 이하에서 `/var/lib/postgresql`에 마운트하면 컨테이너를 다시 만들 때 데이터가 남지 않는다고 문서가 경고한다. 태그만 17로 내리고 마운트 경로를 그대로 두면 down 실험과 정반대 결과가 나온다.

## 이미지 태그 확인 기록 (2026-11-15)

| 태그 | 결과 |
|---|---|
| `postgres:18.6` | 지원 태그 목록의 18 계열은 `18.7`·`18`(및 변형)뿐. 재현은 18.6으로 했다 |
| `redis:8.10-alpine` | 지원 태그 목록 `8.10.3-alpine` 묶음에 포함 |
| `axllent/mailpit:v1.27` | Docker Hub 태그 API에 존재(last_updated 2025-11-08) |

## 출처

- Docker Hub, postgres 공식 이미지 — https://hub.docker.com/_/postgres
- Docker Docs, docker compose up — https://docs.docker.com/reference/cli/docker/compose/up/
- Docker Docs, docker compose down — https://docs.docker.com/reference/cli/docker/compose/down/
- Docker Docs, docker compose ps — https://docs.docker.com/reference/cli/docker/compose/ps/
- Docker Docs, Control startup and shutdown order in Compose — https://docs.docker.com/compose/how-tos/startup-order/
- Docker Docs, Compose services 레퍼런스 — https://docs.docker.com/reference/compose-file/services/
- Docker Docs, Compose version and name — https://docs.docker.com/reference/compose-file/version-and-name/
- Docker Docs, Networking in Compose — https://docs.docker.com/compose/how-tos/networking/
- Docker Docs, Compose 변수 치환 — https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
- PostgreSQL, pg_isready — https://www.postgresql.org/docs/current/app-pg-isready.html
- Spring Boot, Externalized Configuration — https://docs.spring.io/spring-boot/reference/features/external-config.html

## 한계

- 장면은 macOS Docker Desktop 한 환경에서 본 것이다. Windows·WSL2에서는 다시 확인하지 않았다.
- 첫 기동 "10초 안팎"은 `up -d` 출력을 지켜본 관찰값이고 반복 측정 평균이 아니다. 볼륨 상태·머신 부하에 따라 달라진다.
- 포트 점유 재현은 Docker 없이 포트 점유만 만든 것이다. `com.docker.backend`는 Mac Docker Desktop에서 본 이름이고 이 재현에는 나오지 않는다.
- `postgres:18.6`은 확인일 기준 지원 태그 목록에서 빠져 있다. 새로 따라 할 때는 같은 18 계열 최신 패치 태그를 써도 경로는 같다.
