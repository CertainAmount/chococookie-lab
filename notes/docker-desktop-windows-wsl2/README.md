---
title: "Docker Desktop 윈도우 11 Home 설치: WSL2 백엔드로 쓰며 막힌 4곳"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3008
---

# Docker Desktop Windows 요구 사항 — 공식 문서 대조

Docker Desktop Windows 설치 문서와 릴리스 노트가 같은 항목(WSL 최소 버전, 지원 에디션)을 서로 다르게 적고 있는지 2026-11-16에 대조했다. 글의 메모리 그림(32GB PC의 WSL VM 천장)에 쓴 원수치도 함께 둔다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 공식 문서 대조표, 4.97~4.99 Windows 관련 변경, `.wslconfig` 기본값 출처 |
| `figure-data.csv` | 메모리 천장 그림의 원수치(전체 램, 기본 천장 계산값, 저자 설정값) |
| `figures/` | 글에 들어간 도식 PNG(설치 뒤 확인 순서, 설치 모드 갈림길, 메모리 천장) |

## 수집 방법과 기준일

- 기준일: 2026-11-16. Docker Desktop 최신 버전은 4.99.0(2026-11-09 릴리스).
- Docker 설치 문서는 렌더링한 페이지에서 「System requirements」의 WSL 2 백엔드(x86_64) 탭과 같은 페이지의 에디션 문단을 직접 읽었다.
- 릴리스 노트는 4.97.0, 4.98.0, 4.99.0 항목 중 Windows·WSL·설치 관련 줄만 골랐다.
- Microsoft WSL 설정 문서는 2026-10-16 갱신본 기준이다.

## 1. 설치 문서와 릴리스 노트가 어긋나는 곳

| 항목 | 설치 문서(System requirements) | 같은 페이지 다른 절 / 릴리스 노트 | 대조 결과 |
|---|---|---|---|
| WSL 최소 버전 | WSL 2.1.5 이상(Enhanced Container Isolation은 2.6 이상) | 릴리스 노트 4.98.0: WSL 2 백엔드 컨테이너 보안 수정 때문에 WSL 3.0.3 이상 필요 | 설치 문서가 4.98.0 변경을 반영하지 않았다. 최신 버전 기준으로는 3.0.3이 맞다 |
| 지원 에디션 | Windows 11 Enterprise·Pro·Education 23H2(빌드 22631) 이상, Windows 10 Enterprise·Pro·Education 22H2(빌드 19045) 이상. Home 없음 | 같은 페이지: Windows 컨테이너는 Pro·Enterprise 필요, Home·Education은 Linux 컨테이너만 실행 가능 | 요구 목록만 보면 Home이 빠졌지만, 같은 페이지가 Home에서 Linux 컨테이너 실행을 전제로 적고 있다 |

그 밖의 요구 사항(설치 문서): SLAT 지원 64비트 프로세서, 램 8GB, BIOS/UEFI 하드웨어 가상화 켜짐, Windows LanmanServer 서비스 자동 시작.

## 2. 4.97.0~4.99.0 Windows 관련 변경

| 버전 | 변경 |
|---|---|
| 4.97.0 | 새 .EXE 설치는 per-user가 기본. 설치 Configuration 화면에서 백엔드를 고른다(per-user: WSL 2, Docker VMM(Beta) / all-users: WSL 2, Hyper-V, Docker VMM(Beta)). 고를 수 있는 백엔드가 하나면 자동 선택. 느린 WSL 버전 확인 때문에 이미 최신인데도 WSL 업데이트를 요구하던 문제 수정 |
| 4.98.0 | WSL 2 백엔드에 WSL 3.0.3 이상 필요. Docker VMM 엔진일 때 WSL 배포판에서 docker·compose 실행 지원 |
| 4.99.0 | 이미 WSL 2가 되는 PC에서 per-user 설치·업데이트가 「Virtual Machine Platform」 오류로 실패하던 문제 수정. 느린 PC에서 WSL 2 엔진 시작이 실패하던 문제 수정 |

설치 모드 관련(설치 문서): per-user 설치는 Windows 컨테이너와 Hyper-V 백엔드를 쓸 수 없고, Windows Hypervisor Platform은 관리자가 먼저 켜야 한다. WSL 2를 처음 켤 때는 관리자 권한이 한 번 필요하다. 모드를 바꾸려면 제거 후 재설치해야 한다. `docker-users` 그룹은 all-users 설치에서 설치 계정과 사용 계정이 다를 때만 필요하고, WSL 2 Linux 컨테이너에는 필요 없다.

## 3. `.wslconfig` 기본값(그림 원수치의 근거)

| 키 | 기본값(Microsoft 문서) | 32GB PC에 적용하면 |
|---|---|---|
| `memory` | Windows 전체 메모리의 50% | 16GB |
| `swap` | Windows 메모리의 25%, GB 단위 올림 | 8GB |
| `processors` | 논리 프로세서 전부 | — |
| `autoMemoryReclaim`(`[experimental]`) | `dropCache` | — |

변경은 모든 배포판이 멈추고 약 8초 뒤 반영된다. 파일이 없거나 형식이 틀리면 설정 없이 정상 실행된다.

## 출처

- Docker, 「Install Docker Desktop on Windows」 — https://docs.docker.com/desktop/setup/install/windows-install/
- Docker, 「Docker Desktop release notes」 — https://docs.docker.com/desktop/release-notes/
- Docker, 「Docker VMM」 — https://docs.docker.com/desktop/features/vmm/
- Microsoft Learn, 「Advanced settings configuration in WSL」 — https://learn.microsoft.com/en-us/windows/wsl/wsl-config

## 한계

- 대조는 2026-11-16 하루의 문서 상태다. Docker Desktop은 릴리스가 잦아 설치 문서의 WSL 최소 버전 표기가 이후 고쳐질 수 있다.
- 메모리 그림의 16GB는 측정값이 아니라 32GB × 50% 계산값이다.
- Home 에디션 동작은 Windows 11 Home 한 대, WSL 2 백엔드, Linux 컨테이너 조건에서만 확인한 결과다. Hyper-V 백엔드·Windows 컨테이너·Docker VMM은 확인 범위 밖이다.
