---
title: "Docker 장점, 2019년부터 써 보니 남은 셋: 셋업 반나절→20분·태그 하나로 롤백·서버 한 대에 API 둘"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3034
---

# Docker 장점 글 — 재현 스크립트·로그와 도식 원수치

이 노트는 글에서 Docker 없이 재현한 두 가지(컨테이너가 호스트 커널을 공유한다, exec format error는 CPU 아키텍처 문제다)의 스크립트와 원로그, 그리고 도식에 쓴 값을 모은다. 저자 Mac·운영 서버의 값은 저자가 보고한 실측이고, 재현은 별도의 리눅스 PC에서 했다. 두 종류의 값은 서로 다른 기계에서 나왔다.

## 파일

| 파일 | 내용 |
|---|---|
| `repro.sh` | 재현 0~3단계 셸 스크립트(환경 기록, unshare 격리, AArch64 실행, VM 가능 여부) |
| `make_elf_aarch64.py` | 실행 코드 없이 ELF64 헤더만 있는 AArch64(e_machine=183) 파일 생성 |
| `logs/r0-env.log` | 재현 환경: `uname -m`, `uname -r`, OS, 실행 시각 |
| `logs/r1-unshare.log` | namespace 셸 안의 `id`, `uname -r`, `ps` 출력 |
| `logs/r1-time.log` | 그냥 `true`와 `unshare`로 감싼 `true`의 실행 시간(각 3회) |
| `logs/r2-exec-C.log` | AArch64 파일 실행 결과(영어 로캘) |
| `logs/r2-exec-ko.log` | 기본(한국어) 로캘 출력. 처음 셸에서 실행해 줄 번호(30)가 `repro.sh`와 다름 |
| `figure-1-times.csv` | 셋업 시간·Gradle 빌드 시간 막대 차트의 원수치 |
| `figure-2-values.csv` | 세 환경 층 비교 도식에 쓴 값 |
| `figures/` | 본문에 실린 도식·터미널 캡처 PNG |

## 재현 환경과 방법

| 항목 | 값 |
|---|---|
| OS | Ubuntu 22.04.3 LTS |
| CPU 아키텍처 | x86_64 |
| 커널 | 6.8.0-138-generic |
| 실행 시각 | 2026-11-16 03:40 (KST) |
| Docker·sudo | 없음 |
| binfmt_misc | 활성, aarch64 핸들러 없음 |
| /dev/kvm | 있음, qemu 없음 |

- **재현 1(namespace).** `unshare --user --map-root-user --pid --fork --mount-proc`로 셸을 띄우고 안에서 `id`, `uname -r`, `ps`를 실행했다. 안에서는 uid 0(root), PID 1부터 시작하는 프로세스 목록이 보이고, 커널 버전은 바깥과 같다. 시간은 `/usr/bin/time -f "%e"`로 쟀고 해상도는 0.01초다. 여섯 번 모두 0.00초로, 격리 자체의 비용은 해상도 아래였다.
- **재현 2(exec format error).** `make_elf_aarch64.py`로 AArch64용 ELF 헤더 파일을 만들어 x86_64에서 실행했다. aarch64 에뮬레이션 핸들러가 없어 커널이 거부했고 종료 코드는 126이다. `bash: line 1:` 접두는 `bash -c`로 실행했을 때 붙는 실제 출력이다.
- **재현 3(VM 기동 시간).** qemu가 없어 측정하지 않았다. 글에도 VM 부팅 수치는 없다.

## 저자 보고값의 조건

| 값 | 조건 |
|---|---|
| 셋업 20분 안쪽(pull 8분쯤) | 최근 합류자 2명. 클론·`.env` 복사·이미지 pull·첫 `docker compose up -d` 포함 |
| 셋업 반나절~하루 | Docker 이전, 위키 설치 문서로 PostgreSQL·Redis·메일 서버 설치 |
| Gradle 1분 안쪽 → 3분 가까이 | M1 Mac 시절 Spring Boot 프로젝트, 소스와 `~/.gradle` bind mount. VirtioFS 이후 재측정 없음 |
| `docker run --rm alpine true` 0.6~0.9초 | 저자 Mac, 이미지를 받아 둔 상태, Docker Desktop VM이 떠 있을 때 |
| 유휴 VM 1.5GB 안팎 | 저자 Mac(32GB), Docker Desktop VM 할당 8GB·CPU 6, 컨테이너 0개, 2026-11-16 |

## 출처

- Docker Docs — Docker Desktop license agreement: https://docs.docker.com/subscription/desktop-license/
- Docker — Pricing FAQ: https://www.docker.com/pricing/faq/
- Docker Docs — Linux post-installation steps: https://docs.docker.com/engine/install/linux-postinstall/
- Docker Docs — Docker Engine security: https://docs.docker.com/engine/security/
- Docker 블로그 — File Sharing with Docker Desktop (2022-01-24): https://www.docker.com/blog/file-sharing-with-docker-desktop/
- Docker 블로그 — Docker Desktop 4.6 for Mac (2022-03-16): https://www.docker.com/blog/speed-boost-achievement-unlocked-on-docker-desktop-4-6-for-mac/

### Docker Desktop 무료 조건 대조 (2026-11-16 확인)

| 출처 | 문구 |
|---|---|
| 라이선스 문서 | "fewer than 250 employees AND less than $10 million in annual revenue" |
| Pricing FAQ | "fewer than 250 employees AND less than $10M in revenue" |
| 약관 4.2(a) | "fewer than 250 employees and less than US $10,000,000" |

세 곳 모두 무료 조건을 「미만」으로 적는다. 따라서 유료 대상은 직원 250명 이상 또는 연매출 1천만 달러 이상인 기업이다. 정확히 250명이거나 1천만 달러인 회사도 유료 대상에 든다.

## 한계

- 재현은 Docker가 없는 리눅스 PC에서 했다. Docker 컨테이너는 namespace에 cgroups와 이미지·네트워크·볼륨 관리가 더해지므로, 재현 1의 0.00초를 Docker 컨테이너 기동 시간으로 읽으면 안 된다.
- 재현 2의 파일은 헤더만 있어 aarch64 환경에서도 정상 실행되는 프로그램이 아니다. 아키텍처 검사에서 거부되는지만 확인한다.
- 저자 보고값은 표본이 작다(셋업은 2명, 빌드는 한 프로젝트). 팀 평균이나 현재 Docker Desktop 성능으로 일반화하지 않는다.
