#!/usr/bin/env bash
# Docker Hub pull 한도 헤더 확인.
# 익명 토큰을 받아 manifest를 HEAD로 요청하고 ratelimit 헤더만 출력한다.
# 토큰은 변수에만 담고 화면에 찍지 않는다. 기준 IP 줄은 가린다.
# Docker 문서 기준 HEAD 요청은 pull 횟수에 들어가지 않는다.
#
# 사용: ./check_ratelimit.sh [이미지]   (기본: ratelimitpreview/test)
# 로그인 상태 값을 보려면 DOCKERHUB_USER와 액세스 토큰 환경 변수 DOCKERHUB_PAT를 지정한다.
set -euo pipefail

IMAGE="${1:-ratelimitpreview/test}"

AUTH=()
if [[ -n "${DOCKERHUB_USER:-}" ]]; then
  AUTH=(-u "${DOCKERHUB_USER}:${DOCKERHUB_PAT:?DOCKERHUB_PAT 필요}")
fi

TOKEN=$(curl -s ${AUTH[@]+"${AUTH[@]}"} \
  "https://auth.docker.io/token?service=registry.docker.io&scope=repository:${IMAGE}:pull" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')

curl -s --head -H "Authorization: Bearer ${TOKEN}" \
  "https://registry-1.docker.io/v2/${IMAGE}/manifests/latest" \
  | tr -d '\r' \
  | grep -i -E '^(HTTP|date|ratelimit|docker-ratelimit-source)' \
  | sed -E 's/^docker-ratelimit-source:.*/docker-ratelimit-source: <masked>/'
