---
title: "AWS Docker 배포, EC2 Amazon Linux 2023에서 막힌 docker.sock 권한·compose 없음·exec format error"
checked: 2026-11-15
article_url: https://jjeongil.tistory.com/3079
---

# EC2 Amazon Linux 2023 Docker 재현 노트

2026년 11월 초 서울 리전 EC2 t3.micro(Amazon Linux 2023)에서 Docker 설치부터 정리까지 한 바퀴 돈 재현의 명령 순서, AL2·AL2023·Ubuntu 명령 대조, exec format error 재현 방법, 실습 비용 단가, 요금·서비스 출처 대조를 모았다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 이 노트. 재현 런북, 명령 대조, 비용 계산, 출처 대조 |
| `command-comparison.csv` | AL2 / AL2023 / Ubuntu 단계별 명령 대조 |
| `practice-cost-unit-prices.csv` | 서울 t3.micro·t3.small, 퍼블릭 IPv4, Lightsail Nano 단가와 확인일·출처 |
| `exec-format-error-demo.md` | x86 리눅스에서 arm64로 표시된 실행 파일을 실행한 재현 방법 |
| `exec-format-error-demo.txt` | 위 재현의 터미널 출력 원문 |
| `figures/` | 글에 쓴 도식·터미널·공개 페이지 캡처 원본(업로드 스크립트가 채운다) |

## 1. 재현 환경

| 항목 | 값 |
|---|---|
| 시점 | 2026년 11월 초 |
| 리전 | ap-northeast-2(서울) |
| 인스턴스 | t3.micro(x86_64, 2 vCPU, 1 GiB) |
| AMI | Amazon Linux 2023 |
| 기본 사용자 | `ec2-user` |
| 보안 그룹 인바운드 | 22/tcp 소스 내 IP, 80/tcp 소스 0.0.0.0/0 |
| 주소 | 탄력적 IP 1개 연결 |
| 설치된 Docker | 25.0대(`dnf` 저장소) |
| Compose 플러그인 | v5.6.0(수동 설치) |

## 2. 재현 런북 (명령 순서)

```bash
# 접속
chmod 400 my-key.pem
ssh -i my-key.pem ec2-user@<탄력적 IP>

# Docker 설치와 데몬 시작
sudo dnf install -y docker
sudo systemctl enable --now docker

# 그룹 추가 (기존 창은 열어 둔 채 새 창으로 재접속)
sudo usermod -aG docker ec2-user
id            # 새 세션에서 docker 그룹 확인
docker ps

# Compose 플러그인 (Docker 공식 수동 설치 문서 순서, 시스템 경로)
docker compose version     # 설치 전: docker: 'compose' is not a docker command.
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/download/v5.6.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
ls -l /usr/local/lib/docker/cli-plugins/docker-compose   # 수십 MB인지 확인. 수 KB면 404 HTML
docker compose version     # Docker Compose version v5.6.0

# 비공개 이미지 로그인 (둘 중 하나)
echo "$GHCR_TOKEN" | docker login ghcr.io -u <GitHub 사용자명> --password-stdin
aws ecr get-login-password --region ap-northeast-2 \
  | docker login --username AWS --password-stdin <계정 ID>.dkr.ecr.ap-northeast-2.amazonaws.com

# 첫 실행 (플랫폼 미지정 arm64 이미지 → 실패)
docker run -d --name app --restart unless-stopped -p 80:80 ghcr.io/<계정>/<이미지>:<태그>
docker ps          # 비어 있음
docker ps -a       # Exited (255)
docker logs app    # exec /usr/local/bin/docker-entrypoint.sh: exec format error

# Mac에서 amd64로 다시 빌드
docker buildx build --platform linux/amd64 -t ghcr.io/<계정>/<이미지>:<태그> --push .

# EC2에서 다시 받고 확인
docker rm app
docker pull ghcr.io/<계정>/<이미지>:<태그>
docker image inspect --format '{{.Architecture}}' ghcr.io/<계정>/<이미지>:<태그>   # amd64
docker run -d --name app --restart unless-stopped -p 80:80 ghcr.io/<계정>/<이미지>:<태그>
curl -I localhost
```

정리는 콘솔에서 했다: 인스턴스 terminate → EBS 볼륨 목록(비어 있음) → 탄력적 IP 릴리스 → 스냅샷·AMI 확인(없음) → 다음 날·이틀째 Cost Explorer 일 단위·서비스별 확인.

`docker run` 직후에는 아래 경고가 먼저 나왔다.

```text
The requested image's platform (linux/arm64/v8) does not match the detected host platform (linux/amd64/v3) and no specific platform was requested
```

## 3. AL2 / AL2023 / Ubuntu 명령 대조

전체 표는 `command-comparison.csv`. 요약:

| 단계 | Amazon Linux 2 | Amazon Linux 2023 | Ubuntu |
|---|---|---|---|
| 설치 | `amazon-linux-extras install docker` 또는 `yum install docker` | `dnf install -y docker` | Docker apt 저장소 추가 후 `docker-ce`, `docker-compose-plugin` 등 |
| 시작·자동 시작 | `service docker start` + `systemctl enable docker` | `systemctl enable --now docker` | 패키지 설치 시 데몬 시작 |
| Compose | 수동 설치 | 수동 설치(`dnf`로 깐 Docker에는 없었음) | `docker-compose-plugin` 패키지 |
| 기본 사용자 | `ec2-user` | `ec2-user` | `ubuntu` |
| 지원 | 2026-06-30 종료 | 현행 | — |

- `amazon-linux-extras`는 AL2 전용 도구라 AL2023에는 없다.
- AL2023의 `yum`은 `dnf`로 연결돼 있어 그대로 동작한다.
- Ubuntu 열은 Docker 공식 설치 문서(https://docs.docker.com/engine/install/ubuntu/) 기준이다. 저자의 Ubuntu 운영 서버에서 쓴 설치 명령 원문은 아니다.

## 4. exec format error 재현

EC2 원 화면과 별개로, 이 노트 작성 PC(x86_64 리눅스)에서 같은 계열 오류를 재현했다. 방법은 `exec-format-error-demo.md`, 출력은 `exec-format-error-demo.txt`.

- Docker를 쓴 재현이 아니다. `/bin/true` 복사본의 ELF 헤더 기계 종류(e_machine, 오프셋 18)만 aarch64(0xB7)로 바꿔 실행했다.
- 결과는 `cannot execute binary file: Exec format error`. 커널이 다른 아키텍처용 실행 파일을 거부한다는 점은 컨테이너 엔트리포인트가 죽는 원인과 같다.

## 5. 실습 비용 계산

단가는 `practice-cost-unit-prices.csv`. 서울 EC2 단가는 AWS 요금 페이지가 쓰는 공식 데이터 파일(게시 2026-11-14T01:29Z)에서 읽었다.

- 데이터 경로: `https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/ec2/USD/current/ec2-ondemand-without-sec-sel/Asia%20Pacific%20(Seoul)/Linux/index.json`

계산식: `t3.micro 시간당 단가 × 켜 둔 시간 + 루트 EBS 볼륨 + 퍼블릭 IPv4 시간당 요금 × 시간`

| 켜 둔 시간 | t3.micro | 퍼블릭 IPv4 | 합계(EBS 제외) |
|---|---|---|---|
| 1시간 | 0.013 | 0.005 | 0.018 |
| 3시간 | 0.039 | 0.015 | 0.054 |
| 5시간 | 0.065 | 0.025 | 0.090 |
| 24시간 | 0.312 | 0.120 | 0.432 |

단위는 달러. t3.small은 시간당 0.026달러, 730시간 기준 18.98달러(약 19달러)다.

## 6. 요금·서비스 출처 대조 (2026-11-15 확인)

| 항목 | 이전 서술·서드파티 값 | 공식 확인 값 | 출처 |
|---|---|---|---|
| 프리 티어 | 12개월·매달 750시간(2025-07-15 이전 계정 규정) | 2025-07-15 이후 계정: 가입 100달러 + 활동 5개 × 20달러, 최대 200달러, 무료 플랜 6개월 | AWS 한국 블로그 「AWS 프리 티어 업데이트」 https://aws.amazon.com/ko/blogs/korea/aws-free-tier-update-new-customers-can-get-started-and-explore-aws-with-up-to-200-in-credits |
| t3.micro 프리 티어 적격 | — | 적격 | EC2 프리 티어 사용량 https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/ec2-free-tier-usage.html |
| 퍼블릭 IPv4 | — | 2024-02-01부터 시간당 0.005달러, 연결된 주소와 미연결 탄력적 IP 모두 | AWS News Blog https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/ |
| Lightsail 컨테이너 Nano | 서드파티 수치 월 7달러 | 월 7달러, 0.25 vCPU, 512MB(같음) | Lightsail 요금 https://aws.amazon.com/lightsail/pricing/ |
| ECS Express Mode | — | 추가 요금 없음, 바탕 자원(Fargate·ALB 등)만 과금 | ECS 개발자 안내서 https://docs.aws.amazon.com/AmazonECS/latest/developerguide/express-service-overview.html , App Runner 이전 안내 원문 |
| App Runner | 상위 글에 추천이 남아 있음 | 신규 고객 불가, 기존 고객 계속 사용, ECS Express Mode 권장 | AWS App Runner availability change https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html |
| App Runner 중단 날짜 | — | 2026-04-30(보조 근거) | 위 공식 페이지에는 날짜가 없다. docs.aws.amazon.com으로 한정한 검색 요약에 인용된 공지 문구로만 확인해 글 본문에는 넣지 않았다 |
| AL2 지원 종료 | — | 2026-06-30 | Amazon Linux 2 FAQ https://aws.amazon.com/amazon-linux-2/faqs/ |
| 루트 EBS DeleteOnTermination | — | 루트 볼륨 기본 true, 추가 볼륨 기본 false | EC2 사용 설명서 https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/preserving-volumes-on-termination.html |
| ECR 인증 토큰 | `aws ecr get-login`(폐기) | `get-login-password`, 토큰 12시간 | ECR 레지스트리 인증 https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html , CLI v1 레퍼런스 |
| Compose v5.6.0 | — | GitHub 릴리스 존재, 자산 타임스탬프 2026-10-02T15:41Z | https://github.com/docker/compose/releases/tag/v5.6.0 |

## 한계

- 재현 날짜는 「11월 초」, 켜 둔 시간은 「몇 시간」까지만 기록돼 있어 실제 청구액을 단가로 역산하지 않았다. 5절 표는 단가 곱셈이다.
- 루트 EBS 볼륨 단가는 확인하지 않아 5절 합계에서 뺐다.
- AL2023 `dnf` 저장소 전체에 Compose 플러그인 패키지가 없는지는 공식 패키지 목록으로 확인하지 못했다. 재현 출력이 보여 주는 범위는 「`dnf install docker`로 깐 Docker에서 `docker compose`가 없었다」까지다.
- 요금 값은 2026년 11월 기준이며 바뀔 수 있다.
