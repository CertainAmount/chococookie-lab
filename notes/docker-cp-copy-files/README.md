---
title: "docker cp 명령어로 폴더를 두 번 복사하면 conf/conf가 생기는 원인 — 대상 디렉터리가 이미 있으면 폴더째 들어간다"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3032
---

# docker cp 경로 규칙과 관련 근거 — 원문 대조 노트

본문의 경로 해석 표·소유권 표·`docker compose cp` 옵션·nginx 로그 설명이 어느 공식 문구에 기대는지 원문과 한 줄씩 맞춰 둔 노트다. 와일드카드 동작처럼 1차 출처를 찾지 못한 항목은 무엇을 확인했고 무엇이 비어 있는지 따로 적었다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 원문 대조표, `docker compose cp` 옵션, nginx 로그 링크 근거, 와일드카드 미확인 메모 |
| `figures/` | 본문 도식 3장(경로 분기 흐름, 서비스 이름과 컨테이너 이름, cp로 고친 파일의 수명) |

## 수집 방법과 기준일

- 기준일: 2026-11-16.
- Docker 문서 두 쪽(`docker container cp`, `docker compose cp`), nginx 공식 이미지 빌드 Dockerfile, PostgreSQL 백업 문서를 웹에서 직접 열어 해당 문구를 확인했다.
- 경로 분기 결과는 이 문서 규칙 기준이다. 표의 칸마다 터미널에서 재현해 기록한 값이 아니다.

## 1. `docker container cp` 경로 해석 규칙 — 원문 대조

문서는 `SRC_PATH`가 파일인지 디렉터리인지로 나눈 뒤 `DEST_PATH` 상태별 결과를 적는다.

| SRC | DEST 상태 | 문서 원문(요지) | 본문 표 표기 |
|---|---|---|---|
| 파일 | 없음 | the file is saved to a file created at `DEST_PATH` | 그 경로에 파일로 저장 |
| 파일 | 없음, 끝이 `/` | Error condition: the destination directory must exist | 오류 — 대상 디렉터리가 있어야 함 |
| 파일 | 파일로 존재 | the destination is overwritten with the source file's contents | 대상 파일을 덮어씀 |
| 파일 | 디렉터리로 존재 | the file is copied into this directory using the basename from `SRC_PATH` | 그 안에 원본 파일 이름으로 |
| 디렉터리 | 없음 | `DEST_PATH` is created as a directory and the contents of the source directory are copied into this directory | 대상 이름으로 만들어지고 내용이 들어감 |
| 디렉터리 | 파일로 존재 | Error condition: cannot copy a directory to a file | 오류 |
| 디렉터리, `/.`로 끝나지 않음 | 디렉터리로 존재 | the source directory is copied into this directory | 폴더째 그 안에 |
| 디렉터리, `/.`로 끝남 | 디렉터리로 존재 | the content of the source directory is copied into this directory | 내용만 그 안에 |

같은 문서에서 함께 확인한 규칙:

| 항목 | 문서 원문(요지) |
|---|---|
| 상위 디렉터리 | 대상 경로의 상위 디렉터리는 만들어 주지 않는다. 끝이 `/`인 대상은 이미 있어야 한다 |
| 소유권 | Ownership is set to the user and primary group at the destination. 컨테이너로 넣은 파일은 root의 UID:GID, 호스트로 꺼낸 파일은 명령을 실행한 사용자의 UID:GID |
| `-a`, `--archive` | 대상 쪽이 아니라 원본 쪽 사용자·그룹으로 소유권을 맞춘다 |
| 권한 | 디렉터리는 재귀 복사, 권한은 가능한 한 보존(Unix `cp -a`와 비슷) |
| 멈춘 컨테이너 | The CONTAINER can be a running or stopped container |
| 복사 불가 경로 | `/proc`, `/sys`, `/dev` 아래 리소스, tmpfs, 컨테이너 안에서 사용자가 만든 마운트. `docker exec`로 `tar`를 직접 돌리면 복사할 수 있다 |
| `-` | `SRC_PATH`가 `-`면 표준 입력의 tar 아카이브를 대상 디렉터리에 푼다. `DEST_PATH`가 `-`면 대상을 tar 아카이브로 표준 출력에 낸다 |
| 심볼릭 링크 | 기본은 링크 자체를 복사한다. `-L`, `--follow-link`면 원본 쪽 링크가 가리키는 대상을 복사한다 |

## 2. `docker compose cp` 옵션

사용법: `docker compose cp [OPTIONS] SERVICE:SRC_PATH DEST_PATH|-` 또는 `docker compose cp [OPTIONS] SRC_PATH|- SERVICE:DEST_PATH`. 컨테이너 이름 대신 compose 파일의 서비스 이름을 받는다.

| 옵션 | 문서 설명 | 메모 |
|---|---|---|
| `--index` | Index of the container if service has multiple replicas | 문서 표의 기본값 칸은 비어 있다 |
| `--all` | Include containers created by the run command | `docker compose run`으로 만든 컨테이너 포함 |
| `-a`, `--archive` | Archive mode (copy all uid/gid information) | `docker container cp`의 `-a`와 같은 뜻 |
| `-L`, `--follow-link` | Always follow symbol link in SRC_PATH | `docker container cp`의 `-L`과 같은 뜻 |

## 3. nginx 공식 이미지 로그가 파일이 아닌 근거

공식 이미지를 빌드하는 `nginxinc/docker-nginx`의 Dockerfile(mainline/debian)에 다음 단계가 있다.

```dockerfile
ln -sf /dev/stdout /var/log/nginx/access.log \
&& ln -sf /dev/stderr /var/log/nginx/error.log
```

로그 파일 자리가 표준 출력·표준 오류로 가는 심볼릭 링크라서, 컨테이너 안에 로그가 파일로 쌓이지 않는다. `docker cp`는 기본으로 링크 자체를 복사하므로 꺼내도 로그 내용은 없다. 이 로그는 `docker logs`로 본다.

## 4. 실행 중 데이터 디렉터리 복사

PostgreSQL 문서 「File System Level Backup」은 데이터 디렉터리를 파일 단위로 복사하는 방식이 쓸 수 있는 백업이 되려면 서버를 내려야 한다고 적는다. `tar` 같은 도구는 파일시스템의 원자적 스냅샷을 찍지 않고, 서버 내부 버퍼링도 있기 때문이다. 같은 문서는 이 방식이 `pg_dump`보다 실용성이 떨어진다고 정리한다.

## 5. 와일드카드 — 미확인 메모

- 확인한 것: `docker container cp` 문서의 문법은 원본 경로를 하나(`CONTAINER:SRC_PATH` 또는 `SRC_PATH`)만 받는다. 문서는 glob을 언급하지 않는다.
- 찾지 못한 것: `docker cp`가 컨테이너 쪽 `*`를 어떻게 다루는지 적은 1차 출처. 흔히 인용되는 moby 이슈 #33551은 Dockerfile `COPY` 여러 개를 한 레이어로 묶는 이슈(2017년 종료)라 `docker cp` 와일드카드와 관계가 없다. 검색에서 나온 #15858·#29211도 Dockerfile `COPY`의 glob 이슈였다.
- 재현하지 않았다: 확인에 쓴 PC에 Docker가 없었다. 그래서 글에서는 셸 확장이 일어나지 않는다는 구조 설명까지만 하고, 에러 메시지는 싣지 않았다.
- 직접 확인하려면:

```bash
docker run -d --name t nginx
docker cp 't:/etc/nginx/conf.d/*.conf' .   # 따옴표로 호스트 셸 확장을 막는다
docker rm -f t
```

## 출처

- Docker Docs, 「docker container cp」, https://docs.docker.com/reference/cli/docker/container/cp/
- Docker Docs, 「docker compose cp」, https://docs.docker.com/reference/cli/docker/compose/cp/
- nginxinc/docker-nginx, 「mainline/debian/Dockerfile」, https://github.com/nginxinc/docker-nginx/blob/master/mainline/debian/Dockerfile
- PostgreSQL Documentation, 「File System Level Backup」, https://www.postgresql.org/docs/current/backup-file.html
- moby/moby 이슈 #33551(관련 없음 확인용), https://github.com/moby/moby/issues/33551

## 한계

- 경로 분기·소유권은 문서 규칙이며 칸별 재현값이 아니다.
- 문서 원문은 2026-11-16 기준이다. `docker compose cp` 옵션은 Compose 버전에 따라 바뀔 수 있다.
- 와일드카드 동작은 위 5번처럼 1차 출처와 재현이 모두 비어 있다.
