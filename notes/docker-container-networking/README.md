---
title: "도커 컨테이너에서 호스트 localhost 접속 안 될 때, 에러 문구별 해결(host-gateway·0.0.0.0·ufw)"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3050
---

# 컨테이너→호스트 접속 실패: 재현 로그와 에러 문구 대조

컨테이너에서 호스트 서비스(Ollama 11434)를 부를 때 이름·바인드·방화벽 중 어디서 막혔는지 에러 문구로 가를 수 있는지 확인한 기록이다. 본문에서 줄인 재현 명령과 전체 출력, 단계별 문구 대조, 공식 문서 조건을 모았다.

## 파일

| 파일 | 내용 |
|---|---|
| `repro.sh` | 127.0.0.1 바인드와 0.0.0.0 바인드를 호스트의 LAN IP로 호출해 비교하는 스크립트. 마지막에 리눅스 호스트의 `host.docker.internal` 이름 풀이를 확인한다 |
| `repro-output.log` | 위 스크립트를 돌린 출력 전체. LAN IP는 `<LAN IP>`로 가렸다 |
| `env.txt` | 실행 환경(커널, 배포판, Python, curl 버전, 실행 시각) |
| `figures/` | 본문 이미지 원본(진단 흐름도, 경로도, 터미널 캡처) |

## 수집 방법과 기준일

- 바인드 재현: 2026-11-16 11:26 KST, docker가 설치되지 않은 Ubuntu 22.04.3 PC(커널 6.8.0-138, Python 3.11.4, curl 8.1.1). 글의 RTX 4090 워크스테이션과는 다른 머신이다. 컨테이너가 아니라 호스트에서 자기 LAN IP로 호출했다. 목적지 주소가 127.0.0.1이 아니라는 점에서 docker0(172.17.0.1)로 들어오는 연결과 같은 조건이 된다.
- 서버는 `python3 -m http.server`이고 Ollama가 아니다. 응답 본문이 아니라 연결 성공 여부(HTTP 코드, curl 종료 문구)만 본다.
- 실행 전 11434 포트가 비어 있는지 확인했고, 각 단계가 끝나면 서버 프로세스를 종료했다.

## 단계별 에러 문구 대조

| 막힌 곳 | 클라이언트 | 문구 | 어디서 나왔나 |
|---|---|---|---|
| 이름 | aiohttp | `Cannot connect to host host.docker.internal:11434 ssl:default` (줄 앞부분) | 4090 워크스테이션 Open WebUI `docker logs` |
| 이름 | aiohttp 3.8.3 | `ClientConnectorError Cannot connect to host host.docker.internal:11434 ssl:default [Temporary failure in name resolution]` | 네트워크 네임스페이스 재현 |
| 이름 | resolver에 따라 | 괄호 안이 `Name or service not known`으로 바뀌는 환경이 있다 | 네트워크 네임스페이스 재현 |
| 이름 | curl 8.1.1 | `curl: (6) Could not resolve host: host.docker.internal` | 바인드 재현 PC(`repro-output.log`) |
| 바인드 | aiohttp | `Connect call failed ('172.17.0.1', 11434)` | 4090 워크스테이션 `docker logs` |
| 바인드 | aiohttp 3.8.3 | `Cannot connect to host 172.17.0.1:11434 ssl:default [Connect call failed ('172.17.0.1', 11434)]` | 네트워크 네임스페이스 재현 |
| 바인드 | curl 8.1.1 | `curl: (7) Failed to connect to ... port 11434 after 0 ms: Couldn't connect to server` | 네임스페이스 재현, 바인드 재현 PC |
| 방화벽(입력 정책 drop) | curl 8.1.1 | `curl: (28) Connection timed out after 3004 milliseconds` | 네트워크 네임스페이스 재현, `-m 3` 지정 |
| 방화벽 | ufw.log | `IN=docker0`가 찍힌 BLOCK 줄 | 4090 워크스테이션 |
| 컨테이너 간 이름(기본 bridge) | PostgreSQL 클라이언트 | `could not translate host name "pg" to address: Name or service not known` | compose 도입 전 실사건 |

읽는 법: 호스트 이름이 찍히면 이름 단계, IP가 찍히고 바로 실패하면 바인드, 지정한 시간을 다 채우고 실패하면 방화벽(기본 정책이 drop일 때)이다. 방화벽이 reject로 막으면 바로 실패하므로 바인드와 구분되지 않는다. `after 0 ms`의 숫자는 같은 호스트 안 경로라서 0이고, 네트워크를 건너면 몇 ms가 찍힌다.

## 공식 문서 조건 대조 (2026-11-16 확인)

| 조건 | 내용 | 출처 |
|---|---|---|
| `host.docker.internal` 자동 제공 | Docker Desktop이 넣어 준다. 리눅스 Docker Engine에는 없다 | Docker Docs, Docker Desktop networking how-tos — https://docs.docker.com/desktop/features/networking/networking-how-tos/ |
| `host-gateway` 값 | 기본값은 기본 bridge의 IPv4 주소. 데몬 설정 `host-gateway-ip`로 바꾼다. 네트워크별 설정이 아니라 데몬 단위 값이다 | Docker Docs, dockerd 레퍼런스 — https://docs.docker.com/reference/cli/dockerd/ |
| `host-gateway` 도입 버전 | 1차 문서에 도입 버전 표기가 없어 본문에서 버전 조건을 뺐다 | 같은 문서 |
| 기본 bridge 이름 풀이 | 기본 bridge에서는 컨테이너 이름으로 서로를 못 부른다. 사용자 정의 네트워크는 내장 DNS를 쓴다 | Docker Docs, Networking overview — https://docs.docker.com/engine/network/ |
| 브리지 인터페이스 이름 | `com.docker.network.bridge.name`으로 리눅스 브리지 이름을 지정할 수 있다 | Docker Docs, Bridge network driver — https://docs.docker.com/engine/network/drivers/bridge/ |
| publish 포트와 ufw | publish한 포트는 Docker가 넣은 규칙으로 처리돼 ufw 규칙을 건너뛴다 | Docker Docs, Packet filtering and firewalls — https://docs.docker.com/engine/network/packet-filtering-firewalls/ |
| `-p 127.0.0.1:` L2 노출 | 같은 L2 네트워크의 다른 기기가 127.0.0.1로 publish한 포트에 닿던 문제가 Engine 28.0에서 막혔다 | Docker Engine 28.0.0 릴리스 노트(moby/moby#49325) — https://docs.docker.com/engine/release-notes/28/ |
| Ollama 기본 바인드 | 기본 127.0.0.1:11434. `OLLAMA_HOST`로 바꾸고, systemd에서는 `systemctl edit ollama.service`의 `[Service]`에 `Environment`를 넣는다 | Ollama FAQ — https://docs.ollama.com/faq |
| Open WebUI 저장값 | PersistentConfig 설정은 DB 저장값이 환경변수보다 우선한다. `ENABLE_PERSISTENT_CONFIG=False`면 환경변수가 이긴다 | Open WebUI, Environment Variable Configuration — https://docs.openwebui.com/reference/env-configuration/ |

## 한계

- 바인드 재현은 컨테이너가 아니라 호스트에서 LAN IP로 호출한 결과다. docker0 경로 자체는 네트워크 네임스페이스와 veth로 만든 재현으로 확인했고, `docker run` 출력이 아니다.
- 네임스페이스 재현의 서버는 모델 목록 모양 JSON을 돌려주는 파이썬 서버다. Ollama 응답이 아니다.
- timeout 3004 ms는 `-m 3`으로 제한한 값이다. 실제로는 클라이언트 timeout 설정만큼 기다린다.
- 실사건 로그는 줄 앞부분과 핵심 문구만 남아 있어, 괄호 안 전체 문구는 재현값으로 보여 준다.
