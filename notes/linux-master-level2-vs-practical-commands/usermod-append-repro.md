# usermod -G에서 -a 누락 재현 (2026-11-15)

- 목적: 본문 실패담(도커 그룹을 붙이려다 sudo 그룹이 빠진 일)이 명령 동작상 어떻게 일어나는지 보여 준다. 저자의 VPS 사건 자체를 다시 일으킨 것은 아니다.
- 방법: 실제 계정을 건드리지 않도록 임시 폴더에 `etc/passwd·group·shadow·gshadow` 사본을 만들고, 사용자 네임스페이스(`unshare -r`) 안에서 `usermod -P <임시폴더>`로 그 사본만 고쳤다. 화면의 `sudo usermod …` 표기는 읽기 쉽게 실제 서버의 명령 모양으로 옮긴 것이다.
- 환경: Ubuntu, shadow-utils `usermod`.
- 결과: `usermod -G docker dev`는 보조 그룹 목록을 docker 하나로 **교체**해 sudo에서 dev가 빠진다. `-aG`는 기존 그룹에 **추가**한다. 출력은 `usermod-append-repro.txt`(grep 결과는 실제 출력, `$` 명령 줄은 실제 서버 모양으로 옮겨 적음).
- `.ssh` 권한(`bad ownership or modes`) 재현은 이 PC에 sshd가 없어 하지 않았다.
