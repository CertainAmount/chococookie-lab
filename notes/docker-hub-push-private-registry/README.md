---
title: "Docker Hub push denied는 태그 앞 사용자명 누락, 무료 private 저장소는 1개까지"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3035
---

# Docker Hub pull 한도: 문서 세 곳과 응답 헤더 대조

Docker Hub의 pull 한도 숫자가 Docker 자체 문서끼리도 다르고, 2026-11-16에 직접 받은 비로그인 응답 헤더는 그 어느 쪽과도 맞지 않았다. 이 노트는 출처별 원값, 헤더를 받은 방법, 측정의 한계를 모은다.

## 파일

| 파일 | 내용 |
|---|---|
| `ratelimit-sources.csv` | 한도 수치 출처별 대조(usage 문서, 문서의 헤더 예시, pricing FAQ, Docker 블로그, 응답 헤더). 각 행에 횟수·창 길이(초)·확인일·주소 |
| `check_ratelimit.sh` | 응답 헤더 확인 스크립트. 토큰은 변수에만 담고 출력하지 않으며, 기준 IP 줄은 가린다 |
| `ratelimit-response-2026-11-16.txt` | 2026-11-16 03:29 KST 비로그인 응답 헤더(IP 가림) |
| `figures/` | 글에 쓴 도식·터미널·공개 페이지 캡처 원본 |

## 측정 방법

1. `auth.docker.io`에서 `ratelimitpreview/test`에 대한 익명 pull 토큰을 받는다. 토큰은 셸 변수에만 담는다.
2. 그 토큰으로 `registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest`에 HEAD 요청을 보내고 헤더만 받는다.
3. `ratelimit-limit`, `ratelimit-remaining`, `docker-ratelimit-source` 세 줄을 읽는다.

```bash
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:ratelimitpreview/test:pull" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
curl -s --head -H "Authorization: Bearer $TOKEN" \
  https://registry-1.docker.io/v2/ratelimitpreview/test/manifests/latest
```

- `ratelimit-limit: 100;w=3600`은 "3600초(1시간) 창에 100회"로 읽는다. `w=` 뒤 숫자는 창 길이(초)다.
- `ratelimit-remaining`이 `ratelimit-limit`과 같으면 그 창에서 아직 집계된 pull이 없다는 뜻이다.
- `docker-ratelimit-source`는 한도를 세는 기준 IP다. 공개 로그에서는 가렸다.
- usage 문서는 "GET은 실제 pull처럼 집계되고 HEAD는 집계되지 않는다"고 적는다. 그래서 HEAD로만 확인했다.
- 로그인 상태 값은 첫 줄 `curl -s` 뒤에 `-u 사용자명:액세스토큰`을 붙이면 받을 수 있다. 스크립트에서는 환경 변수로 넘긴다.

환경: Linux, curl, python3. 기준 시각 2026-11-16 03:29 KST(응답 `date` 헤더 2026-11-15 18:29:06 GMT).

## 출처별 결과 요약

| 출처 | 비로그인 | Personal 로그인 |
|---|---|---|
| usage 문서 본문 | 6시간 100회 (IPv4 주소 또는 IPv6 /64) | 6시간 200회 |
| usage 문서 헤더 예시 | `100;w=21600` (6시간) | — |
| pricing FAQ | 시간당 10회 | 시간당 100회 |
| Docker 블로그(2025년 4월) | 시간당 안 미시행, 기존 6시간 한도 유지 | 같음 |
| 응답 헤더(1회) | `100;w=3600` (1시간) | — |

pricing FAQ의 시간당 문구는 Docker가 2025년 4월에 도입하려다 시행하지 않은 안의 숫자다. 블로그가 미시행을 밝힌 뒤에도 FAQ 문구는 2026-11-16 기준 그대로 남아 있다.

## GHCR 과금 문구 대조 (2026-11-16)

- GitHub Packages 과금 문서: "Container image storage and bandwidth for the Container registry is currently free." 변경 시 최소 1개월 전에 알린다.
- 같은 문서와 요금제 안내: GitHub Free의 Packages 몫은 저장 500MB·월 전송 1GB(Actions 아티팩트와 공유).
- 문서는 500MB가 Container registry 이미지에 적용되는지를 따로 명시하지 않는다.

## 출처

- Docker Docs, Docker Hub pull usage and limits — https://docs.docker.com/docker-hub/usage/pulls/
- Docker, Pricing FAQ — https://www.docker.com/pricing/faq/
- Docker Blog, Revisiting Docker Hub Policies: Prioritizing Developer Experience — https://www.docker.com/blog/revisiting-docker-hub-policies-prioritizing-developer-experience/
- GitHub Docs, About billing for GitHub Packages — https://docs.github.com/en/billing/concepts/product-billing/github-packages

## 한계

- 응답 헤더는 2026-11-16 03:29 KST에 한 IP에서 한 번 받은 값이다. 이 값만으로 Docker가 한도 창을 1시간으로 바꿨다고 볼 수 없다.
- 측정 IP가 IPv4였는지 IPv6였는지는 기록하지 않았다.
- 로그인 상태 헤더는 측정하지 않았다. Personal 로그인 값은 문서값이다.
- 문서 문구는 확인일 기준이며 이후 바뀔 수 있다.
