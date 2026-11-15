---
title: "도커 컨테이너 이름 already in use 에러, 개발 DB가 든 pg는 rm 대신 start로 살렸다"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3033
---

# 도커 컨테이너 이름 충돌 — 공식 문서 원문 대조

본문에서 결론만 적은 명령 동작(`rm -f`/`-v`, `rename`, `--name`·`--rm`, compose `container_name`, 프로젝트 이름 결정 순서)을 Docker 공식 문서 원문과 나란히 놓았다. 본문의 판단이 문서의 어느 문장에 기대는지 확인하는 용도다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 원문 대조표, 확인 버전, 출처, 한계 |
| `figures/figure-3.png` | already in use 에러에서 start·rename·rm을 가르는 판단 흐름도 |
| `figures/figure-4.png` | compose 프로젝트 이름이 컨테이너·볼륨 이름 앞에 붙는 구조도 |

## 확인 환경과 기준일

- 명령·에러 문구: Docker Desktop 4.96.3, Docker Engine 29.9.2, macOS, 2026-11-15 확인
- 공식 문서 원문: 2026-11-16 조회
- Compose는 V2(`docker compose`) 기준이다. V1(`docker-compose`)은 이름 구분자가 밑줄이었다.

## 원문 대조표

| 항목 | 공식 문서 원문 | 출처 | 이 원문에서 나온 결론 |
|---|---|---|---|
| `rm -f` | "Force the removal of a running container (uses SIGKILL)" | docker container rm | 실행 중이어도 종료 신호 유예 없이 강제로 지운다. 볼륨을 지우는 옵션이 아니다 |
| `rm -v` | "Remove anonymous volumes associated with the container" | docker container rm | 익명 볼륨만 같이 지운다 |
| 이름 붙인 볼륨 | "if a volume was specified with a name, it will not be removed" | docker container rm | named volume은 `rm -v`로도 남는다 |
| `rename` 상태 조건 | "Container may be running, paused or stopped." | docker/cli man 소스 `container/rename.md` | 실행 중·일시정지·정지 모두 이름을 바꿀 수 있다. docs.docker.com 레퍼런스 페이지에는 상태 조건이 적혀 있지 않다 |
| `--name` 생략 | "the daemon assigns a randomly generated name, such as `vibrant_cannon`" | docker container run | 이름을 안 주면 형용사_성 모양의 무작위 이름이 붙는다 |
| `--rm` | "Automatically remove the container and its associated anonymous volumes when it exits" | docker container run | 종료 시 컨테이너와 익명 볼륨이 함께 지워져 이름이 남지 않는다 |
| `container_name`과 scale | "Compose does not scale a service beyond one container if the Compose file specifies a `container_name`. Attempting to do so results in an error." | Compose services reference | `container_name`을 적은 서비스는 한 개 넘게 늘릴 수 없다 |
| 이름에 쓸 수 있는 문자 | `[a-zA-Z0-9][a-zA-Z0-9_.-]+` | Compose services reference | 영문자·숫자로 시작, 이후 영문자·숫자·`_`·`.`·`-` |
| 프로젝트 이름 결정 순서 | 1) `-p` 플래그 2) `COMPOSE_PROJECT_NAME` 3) Compose 파일 최상위 `name:` 4) Compose 파일이 있는 디렉터리 이름 (5번째: 파일을 지정하지 않으면 현재 디렉터리) | Specify a project name | 위에 있는 것이 이긴다. 아무것도 없으면 폴더 이름 |

## 출처

- Docker Docs, docker container rm — https://docs.docker.com/reference/cli/docker/container/rm/
- Docker Docs, docker container run — https://docs.docker.com/reference/cli/docker/container/run/
- docker/cli, man/src/container/rename.md — https://github.com/docker/cli/blob/master/man/src/container/rename.md
- Docker Docs, Compose services reference — https://docs.docker.com/reference/compose-file/services/
- Docker Docs, Specify a project name — https://docs.docker.com/compose/how-tos/project-name/

## 한계

- compose 컨테이너 이름 `프로젝트-서비스-번호`와 볼륨 이름 `프로젝트_볼륨` 규칙은 공식 1차 문서에서 원문을 찾지 못했다. 본문의 근거는 두 폴더에서 `docker compose config`로 출력한 볼륨 이름(`shop-old_pgdata`, `shop-new_pgdata`)이다.
- V1의 밑줄 구분자(`shop_db_1`)는 이번에 공식 문서로 다시 확인하지 않았다.
- postgres 공식 이미지가 데이터 경로에 `VOLUME`을 선언한다는 점은 이번에 Dockerfile을 열어 대조하지 않았다.
