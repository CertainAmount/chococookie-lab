---
title: "Docker 컨테이너 삭제·이미지 삭제: running·conflict 에러 푸는 순서와 prune 세 번으로 4.9GB 비운 기록"
checked: 2026-11-15
article_url: https://jjeongil.tistory.com/3026
---

# Docker prune 회수량과 Docker.raw 크기 측정 노트

같은 Mac에서 `docker system df`, prune 세 단계, `ls -klsh Docker.raw`를 순서대로 잰 원수치와, prune 계열 명령의 기본 범위를 공식 문서·엔진 소스와 맞춰 본 결과를 모았다. 글의 표·차트 숫자가 어디서 왔는지 확인하는 용도다.

## 파일

| 파일 | 내용 |
|---|---|
| `system-df.csv` | 2026-10-11·2026-11-15 `docker system df` 항목별 개수·크기·회수 가능, prune 단계별 직후 값 |
| `prune-steps.csv` | 2026-11-15 prune 명령별 회수량과 합계·대조 계산 |
| `docker-raw.csv` | 2026-11-15 `ls -klsh Docker.raw` 앞 칸(실제 차지)·뒤 칸(겉보기) 3단계 |
| `prune-official-docs.csv` | 명령별 기본 범위·`-a`·볼륨 처리, 에러 문구 형식을 공식 문서·Moby 소스와 대조한 표 |
| `sparse-file-demo.txt` | sparse 파일 재현 명령과 출력 원문 |
| `figures/` | 글에 실린 도식·차트·터미널 이미지 원본 |

## 수집 방법과 기준일

- 환경: macOS, Docker Desktop 4.96.3, Docker Engine 29.9.2(`docker version`의 Server: Docker Desktop 항목과 Desktop 창의 버전 표시로 확인). 기준일 2026-11-15.
- 순서: `docker system df` → `docker builder prune`(`-a` 없이, 확인 프롬프트에 y) → `docker system df` → `docker image prune` → `docker system df` → `docker image prune -a` → `docker system df`. Docker.raw는 정리 전, prune 세 번 직후, Docker Desktop 재시작 뒤에 `ls -klsh`로 쟀다.
- 회수량은 각 prune 명령이 마지막 줄에 찍는 `Total reclaimed space` 값이다.
- 2026-10-11 값은 같은 Mac에서 `docker system df`로 잰 것이고, 그날은 회수 가능 열을 남기지 않았다.
- Finder 표시(같은 날): 목록 크기 64GB, 정보 가져오기의 디스크상 크기 11.4GB. 재시작 전후 중 어느 시점인지 기록이 없어 `docker-raw.csv`에는 넣지 않았다.

## 회수량 산술 대조

| 계산 | 결과 | 측정값 | 판정 |
|---|---|---|---|
| Images 4.12 − image prune 0.41 | 3.71 | image prune 직후 3.71 | 일치 |
| Images 3.71 − image prune -a 2.19 | 1.52 | image prune -a 직후 1.52 | 일치 |
| Build Cache 3.38 − builder prune 2.31 | 1.07 | builder prune 직후 1.07 | 일치 |
| 2.31 + 0.41 + 2.19 | 4.91 | — | 세 명령 합계 |
| image prune 0.41 + image prune -a 2.19 | 2.60 | 정리 전 Images 회수 가능 2.61 | 차이 0.01GB |

- SIZE 합과 회수량 차이: 공유 레이어가 한 번만 빠져서 생긴다(산술 대조는 위 표).

## sparse 파일 재현

Docker.raw가 sparse 파일이라 겉보기 크기(64G)와 실제 차지 크기가 따로 움직인다는 점을 리눅스 PC에서 같은 구조로 재현했다. Docker.raw 자체를 쓴 실험은 아니다.

1. `truncate -s 64G disk.raw` — 겉보기 64G, 실제 0
2. `dd if=/dev/urandom ... count=200 conv=notrunc` — 앞부분 200M 기록, 실제 200M
3. `fallocate --punch-hole --keep-size --offset 0 --length 100M` — 100M 구멍, 실제 100M

세 단계 모두 `ls -lsh`의 뒤 칸은 64G 그대로였다. 원문은 `sparse-file-demo.txt`.

## 출처

- Docker Docs, docker container rm — https://docs.docker.com/reference/cli/docker/container/rm/
- Docker Docs, docker image rm — https://docs.docker.com/reference/cli/docker/image/rm/
- Docker Docs, docker image prune — https://docs.docker.com/reference/cli/docker/image/prune/
- Docker Docs, docker builder prune — https://docs.docker.com/reference/cli/docker/builder/prune/
- Docker Docs, docker system prune — https://docs.docker.com/reference/cli/docker/system/prune/
- Docker Docs, docker volume prune — https://docs.docker.com/reference/cli/docker/volume/prune/
- Docker Docs, docker compose down — https://docs.docker.com/reference/cli/docker/compose/down/
- Docker Docs, Docker Desktop for Mac FAQ — https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/
- Docker Docs, JSON File logging driver — https://docs.docker.com/engine/logging/drivers/json-file/
- Moby, daemon/images/image_delete.go — https://github.com/moby/moby/blob/master/daemon/images/image_delete.go
- Moby, daemon/delete.go — https://github.com/moby/moby/blob/master/daemon/delete.go

## 한계

- Mac 한 대에서 한 번 잰 값이다. 이미지 구성과 빌드 이력이 다르면 회수량은 달라진다.
- Docker.raw 감소량(11G → 8.2G)과 prune 회수 합계(4.91GB)는 크기가 다르다. 둘 사이 차이의 원인은 이 측정으로 가리지 않았다.
- 공식 Mac FAQ는 공간이 몇 초 안에 돌아온다고 적지만, 이 측정에서는 재시작 뒤에야 줄었다. Docker Desktop 버전이 바뀌면 다시 확인해야 한다.
- Moby 소스는 2026-11-15 master 기준이다. 에러 문구는 엔진 버전에 따라 달라질 수 있다.
- json-file 로그 드라이버 항목은 이번에 재조회하지 않았다.
