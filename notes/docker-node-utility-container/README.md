---
title: "Node 설치 없이 도커로 npm 실행 설정 — 유틸리티 컨테이너 한 줄과 root 소유·/.npm EACCES 해결"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3068
---

# 연구 노트: HOME이 `/`일 때 npm 캐시 경로와 `/.npm` EACCES

이 노트는 `-u`로 이미지에 없는 uid를 넘겼을 때 npm이 `/.npm`을 만들다 실패하는 이유를, 호스트에서 HOME을 바꿔 확인한 기록이다. 본문 「`npm_config_cache`로 캐시만 옮긴다」 판단과 터미널 화면의 원자료다.

## 파일

| 파일 | 내용 |
|---|---|
| `repro.sh` | 재현에 쓴 명령을 그대로 모은 스크립트(R1·R2) |
| `env.log` | 재현 환경: Node·npm 버전, 실행 uid |
| `r1.log` | R1 — HOME 값에 따라 `npm config get cache`가 가리키는 경로 |
| `r2.log` | R2 — HOME=`/`에서 `npm install` 실패(EACCES)와 캐시 경로 지정 뒤 성공. `npm notice`(새 버전 안내) 다섯 줄만 지웠다 |

## 방법과 기준일

- 기준일: 2026-11-16
- 환경: Ubuntu 22.04.3, Node v24.21.0, npm 11.19.0, 실행 uid 1000. docker가 없는 PC라 **컨테이너 안에서 돌린 것이 아니다.** `env HOME=/`로 "이미지에 없는 uid로 돌아 HOME이 `/`가 된 상태"를 흉내 냈다.
- R1은 네트워크 없이 설정값만 읽는다. R2는 빈 프로젝트에 `is-number` 하나를 설치한다.
- 본문의 `added 2 packages, and audited 3 packages in 611ms` 출력은 같은 환경에서 저자가 따로 돌린 실행이다. 이 노트의 R2(`added 1 package … in 600ms`, 캐시 경로 `/tmp/.npm-r2`)와 수치가 다르다.

## R1 결과 요약

| 조건 | `npm config get cache` |
|---|---|
| `HOME=/` | `/.npm` |
| `HOME=/tmp` | `/tmp/.npm` |
| `HOME=/` + `npm_config_cache=/tmp/.npm` | `/tmp/.npm` |

캐시 기본값이 `$HOME/.npm`이고, `npm_config_cache`가 HOME보다 우선한다는 것을 보여 준다.

## R2에서 볼 줄

- `syscall mkdir`, `path /.npm` — 폴더를 만들려다 실패했다는 뜻이다. 소유가 아니라 위치 문제다.
- `sudo chown -R 1000:1000 "/.npm"` — 안내에 찍히는 숫자는 명령을 실행한 uid다.
- 캐시 경로만 바꾼 두 번째 실행은 `exit=0`으로 끝난다.

## R4 — esbuild 플랫폼 불일치 재현(성립하지 않아 폐기)

Linux에서 `npm install esbuild --os=darwin --cpu=arm64`로 darwin-arm64용을 받아 실행 오류를 보려 했다. `node_modules/@esbuild/darwin-arm64`는 설치됐지만 postinstall이 npm의 install 스크립트 경고로 막혔고, `transformSync` 호출은 오류 없이 끝났다(exit 0). 플랫폼 불일치 오류가 나오지 않아 본문에는 쓰지 않았다. 본문의 esbuild 사건(linux-x64 → 맥미니)은 저자 경험 서술이며 오류 문구를 인용하지 않는다.

## 원문(2025년 판) 명령 검증

이 URL의 예전 글이 쓰던 명령을 2026-11-16 기준으로 다시 본 결과다.

| 예전 글의 명령·설명 | 확인 결과 | 새 글의 처리 |
|---|---|---|
| `docker run node`가 바로 꺼지는 이유를 "입력을 기다리는 이미지"로 설명 | 기본 명령이 REPL이고 STDIN(`-i`)이 없으면 바로 끝나는 것 | 한 문장으로 바로잡음 |
| `docker run -it node npm init` | 동작함. `-v`·`-w`가 없으면 `package.json`이 컨테이너와 함께 사라짐 | `--rm -v "$PWD":/app -w /app`을 붙인 형태로 교체 |
| `-dit`로 띄운 뒤 `docker exec`로 `npm init` | 동작하지만 컨테이너가 남음 | `--rm` 일회성 실행으로 대체 |
| `docker container prune`으로 정리 | 중지된 컨테이너 전부 삭제 | `--rm`이면 필요 없음, 정리는 별도 글로 연결 |
| `FROM node:14-alpine` 이미지 빌드 | Node 14는 지원 종료. alpine은 musl이라 네이티브 모듈에서 문제 가능 | 이미지 빌드 단계 삭제, 태그는 메이저 숫자 고정 |
| `-v $(pwd):/app` | Linux·WSL에서 생성 파일이 root 소유가 되는 문제 미언급, PowerShell 문법 아님 | root 소유·`-u`·`/.npm` 연쇄로 확장, PowerShell `${PWD}` 추가 |

## 출처

- Node.js Release Working Group, 릴리스 일정(schedule.json): https://github.com/nodejs/Release — 2026-11-16 조회. Node 26 Active LTS(2026-10-28), 24 유지보수(2028-04-30 종료), 22 유지보수(2027-04-30 종료), 20 종료(2026-04-30)
- npm Docs, config — cache: https://docs.npmjs.com/cli/v11/using-npm/config#cache
- nodejs/docker-node, BestPractices: https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md

## 한계

- 모든 실행이 호스트에서 HOME을 바꾼 재현이다. 컨테이너 안에서의 출력은 아니다.
- root 소유가 생기는 단계(rootful Docker)와 맥에서의 소유 표시는 이 PC에 docker가 없어 재현하지 않았다.
- 실행 한 번씩의 기록이라 설치 시간(600ms)은 네트워크 상태에 따라 달라진다.
