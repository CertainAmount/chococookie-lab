#!/usr/bin/env bash
# 127.0.0.1 바인드와 0.0.0.0 바인드의 차이를 호스트에서 자기 LAN IP로 호출해 확인한다.
# 컨테이너 안에서 실행하는 재현이 아니다. docker가 없는 리눅스 PC에서 돌렸다.
# 11434 포트가 비어 있어야 한다. 끝나면 띄운 파이썬 서버를 정리한다.
set -u

ss -tlnp | grep ':11434' || echo "11434 free"          # 포트가 비었는지 먼저
HOSTIP=$(hostname -I | awk '{print $1}')                 # 출력 로그에서는 <LAN IP>로 가렸다

# 1) 127.0.0.1에만 묶기
python3 -m http.server 11434 --bind 127.0.0.1 >/dev/null 2>&1 & PID=$!; sleep 1
ss -tlnp | grep ':11434'
curl -sS -m 3 -o /dev/null -w 'loopback %{http_code}\n' http://127.0.0.1:11434/
curl -sS -m 3 -o /dev/null -w 'lan %{http_code}\n' http://$HOSTIP:11434/
kill $PID; sleep 1

# 2) 0.0.0.0에 묶기
python3 -m http.server 11434 --bind 0.0.0.0 >/dev/null 2>&1 & PID=$!; sleep 1
ss -tlnp | grep ':11434'
curl -sS -m 3 -o /dev/null -w 'lan %{http_code}\n' http://$HOSTIP:11434/
kill $PID

# 3) 리눅스 호스트 자체도 host.docker.internal을 모른다(컨테이너 안이 아님)
getent hosts host.docker.internal; echo "getent exit=$?"
curl -sS -m 3 http://host.docker.internal:11434/ ; echo
