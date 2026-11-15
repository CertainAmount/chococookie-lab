#!/usr/bin/env bash
# Docker 없이 두 가지를 재현한다.
#  1) 컨테이너 = 호스트 커널을 공유하는 격리 프로세스 (namespace만, unshare)
#  2) exec format error = CPU 아키텍처가 다른 실행 파일 (AArch64 ELF 헤더)
# 환경: Ubuntu 22.04.3 LTS, x86_64, 커널 6.8.0-138-generic, docker·sudo 없음
# 빈 작업 디렉터리에서 실행한다. 전부 수 초 안에 끝난다.
set -u

# 0) 환경
{ uname -m; uname -r; . /etc/os-release && echo "$PRETTY_NAME"; date -Is; } | tee r0-env.log

# 1) namespace만으로 격리된 셸 (user + pid + mount-proc)
unshare --user --map-root-user --pid --fork --mount-proc \
  sh -c 'echo "--- inside"; id; uname -r; ps -o pid,comm' 2>&1 | tee r1-unshare.log

# 격리 비용 비교 (각 3회, /usr/bin/time 해상도 0.01초)
for i in 1 2 3; do /usr/bin/time -f "%e s plain" sh -c true; done 2>&1 | tee r1-time.log
for i in 1 2 3; do /usr/bin/time -f "%e s unshare" unshare --user --map-root-user --pid --fork true; done 2>&1 | tee -a r1-time.log
# 'Operation not permitted'(AppArmor 비특권 user namespace 제한)가 나오면 그 출력을 그대로 기록한다.

# 2) AArch64 실행 파일을 x86_64에서 실행
cat /proc/sys/fs/binfmt_misc/status 2>/dev/null
ls /proc/sys/fs/binfmt_misc/ 2>/dev/null | grep -i aarch64 || echo "no aarch64 binfmt handler"
#   qemu-aarch64 binfmt 핸들러가 등록돼 있으면 에뮬레이션으로 실행될 수 있으니 결과를 해석할 때 함께 본다.
python3 -I make_elf_aarch64.py
file hello-arm64 2>/dev/null
# 기본 로캘 출력
{ ./hello-arm64; echo "exit=$?"; } 2>&1 | tee r2-exec-ko.log
# 영어(C) 로캘 출력
LC_ALL=C bash -c './hello-arm64; echo "exit=$?"' 2>&1 | tee r2-exec-C.log

# 3) VM 기동 비용 — 가능 여부만 확인 (이번 환경에서는 qemu가 없어 측정하지 않음)
ls -l /dev/kvm 2>&1; command -v qemu-system-x86_64 || echo "no qemu"
