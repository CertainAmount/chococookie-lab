#!/bin/sh
# 사용: ./platforms.sh library/mysql 5.7  — 토큰은 화면에 찍지 않는다
repo=$1; tag=$2
T=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:$repo:pull" | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
curl -s -H "Authorization: Bearer $T" -H "Accept: application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json" \
  "https://registry-1.docker.io/v2/$repo/manifests/$tag" \
  | python3 -c 'import sys,json;[print(m["platform"]["os"]+"/"+m["platform"]["architecture"]+("/"+m["platform"]["variant"] if m["platform"].get("variant") else "")) for m in json.load(sys.stdin).get("manifests",[]) if m["platform"]["os"]!="unknown"]'
