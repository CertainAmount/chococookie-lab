# chococookie-lab

[쵸코쿠키의 연습장](https://jjeongil.tistory.com/) 글 뒤에 있는 데이터·근거·실측 기록을 모아 둔 저장소입니다.

글 본문은 독자가 답을 얻고 판단하는 데 필요한 결론만 담습니다. 그 결론에 이르기까지 쓴 원자료 표, 수집 방법과 기준일, 출처별 비교, 재현 스크립트와 측정 로그는 여기 글마다 한 폴더씩 정리합니다. 숫자를 직접 확인하거나 실험을 다시 돌려 보고 싶은 분이 보시면 됩니다.

## 폴더

- `notes/<글 슬러그>/` — 글 하나의 연구 노트. `README.md`에 글 링크, 기준일, 수집 방법, 파일 설명, 출처, 한계가 있습니다. 옆에 표(`*.csv`, UTF-8), 스크립트, 로그가 놓입니다.

글 문장은 여기에 옮기지 않습니다. 설명은 각 글에서 읽어 주세요.

## 노트 목록 (최신순)

<!-- notes:start -->
- [Dockerfile ARG vs ENV 차이, FROM 앞 ARG가 스테이지에서 빈 값이 되고 토큰이 docker history에 남은 기록](https://jjeongil.tistory.com/3046) · [연구 노트](notes/dockerfile-arg-vs-env/) · 기준일 2026-11-16
- [Docker Hub push denied는 태그 앞 사용자명 누락, 무료 private 저장소는 1개까지](https://jjeongil.tistory.com/3035) · [연구 노트](notes/docker-hub-push-private-registry/) · 기준일 2026-11-16
- [Docker Desktop 윈도우 11 Home 설치: WSL2 백엔드로 쓰며 막힌 4곳](https://jjeongil.tistory.com/3008) · [연구 노트](notes/docker-desktop-windows-wsl2/) · 기준일 2026-11-16
- [맥북 도커 설치, Mac Docker Desktop을 brew로 깔고 hello-world까지 7분, 그 뒤 막힌 에러 3개](https://jjeongil.tistory.com/3007) · [연구 노트](notes/docker-desktop-mac-install/) · 기준일 2026-11-16
- [docker cp 명령어로 폴더를 두 번 복사하면 conf/conf가 생기는 원인 — 대상 디렉터리가 이미 있으면 폴더째 들어간다](https://jjeongil.tistory.com/3032) · [연구 노트](notes/docker-cp-copy-files/) · 기준일 2026-11-16
- [도커 컨테이너 이름 already in use 에러, 개발 DB가 든 pg는 rm 대신 start로 살렸다](https://jjeongil.tistory.com/3033) · [연구 노트](notes/docker-container-name-conflict/) · 기준일 2026-11-16
- [Docker 코드 수정 반영 안 될 때 원인 확인 순서, 컨테이너 이미지 ID 앞 12자리부터 본다](https://jjeongil.tistory.com/3022) · [연구 노트](notes/docker-build-cache-changes-not-applied/) · 기준일 2026-11-16
- [Docker 장점, 2019년부터 써 보니 남은 셋: 셋업 반나절→20분·태그 하나로 롤백·서버 한 대에 API 둘](https://jjeongil.tistory.com/3034) · [연구 노트](notes/docker-advantages-vs-vm/) · 기준일 2026-11-16
- SQLD 따야 하나, 백엔드 면접관이 서류와 면접에서 본 경계 (발행 전) · [연구 노트](notes/sqld-worth-it-vs-practical-sql/) · 기준일 2026-11-15
- 보조배터리 기내반입 Wh 계산, 20000mAh 라벨에서 읽을 줄과 2개 한도 (발행 전) · [연구 노트](notes/power-bank-carry-on-wh-check/) · 기준일 2026-11-15
- 리눅스마스터 2급 vs 실무 리눅스 명령, 블로그 검색어 4,419클릭을 출제기준에 대 보니 (발행 전) · [연구 노트](notes/linux-master-level2-vs-practical-commands/) · 기준일 2026-11-15
- 아이폰 보상판매 vs 중고폰 판매, 민팃 앱 60만 원 견적이 현장에서 40만 원대가 된 이유 (발행 전) · [연구 노트](notes/iphone-trade-in-vs-used-sale/) · 기준일 2026-11-15
- 힉스필드 요금제·무료 크레딧, Seedance 2.0 영상은 어느 플랜부터인가 — Ultra 한 달 3,000크레딧 써 보니 (발행 전) · [연구 노트](notes/higgsfield-pricing-free-credits/) · 기준일 2026-11-15
- [Docker 컨테이너 삭제·이미지 삭제: running·conflict 에러 푸는 순서와 prune 세 번으로 4.9GB 비운 기록](https://jjeongil.tistory.com/3026) · [연구 노트](notes/docker-container-remove-cleanup/) · 기준일 2026-11-15
- [docker compose up -d 다음 ps -a부터: localhost·healthcheck·포트 충돌, 안 뜨는 원인 3가지](https://jjeongil.tistory.com/3063) · [연구 노트](notes/docker-compose-up-getting-started/) · 기준일 2026-11-15
- [AWS Docker 배포, EC2 Amazon Linux 2023에서 막힌 docker.sock 권한·compose 없음·exec format error](https://jjeongil.tistory.com/3079) · [연구 노트](notes/docker-aws-ec2-deploy/) · 기준일 2026-11-15
<!-- notes:end -->

## 라이선스

- 표·도식·노트: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.ko). 출처로 "쵸코쿠키의 연습장"과 해당 글 링크를 남겨 주세요.
- 스크립트: MIT. 자세한 내용은 [LICENSE](LICENSE).
