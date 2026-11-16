#!/usr/bin/env bash
# HOME이 / 인 상태에서 npm 캐시 경로와 /.npm EACCES를 호스트에서 재현한다.
# 컨테이너 안 실행이 아니다. 빈 작업 폴더에서 돌린다.
set -u

work="$(mktemp -d)"
cd "$work"

# 환경
{
  echo '$ node -v; npm -v; id -u'
  node -v; npm -v; id -u
} > env.log 2>&1

# R1 — HOME에 따라 npm 캐시 경로가 바뀌는지
{
  echo '$ env HOME=/ npm config get cache'
  env HOME=/ npm config get cache
  echo '$ env HOME=/tmp npm config get cache'
  env HOME=/tmp npm config get cache
  echo '$ env HOME=/ npm_config_cache=/tmp/.npm npm config get cache'
  env HOME=/ npm_config_cache=/tmp/.npm npm config get cache
} > r1.log 2>&1

# R2 — HOME=/ 에서 설치 실패, 캐시 경로만 바꿔 성공
mkdir r2 && cd r2 && npm init -y > /dev/null
{
  echo '$ env HOME=/ npm install is-number'
  env HOME=/ npm install is-number
  echo "exit=$?"
  echo '$ env HOME=/ npm_config_cache=/tmp/.npm-r2 npm install is-number'
  env HOME=/ npm_config_cache=/tmp/.npm-r2 npm install is-number
  echo "exit=$?"
} > ../r2.log 2>&1

echo "logs: $work"
