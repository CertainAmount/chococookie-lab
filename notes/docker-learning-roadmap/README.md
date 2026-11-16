---
title: "Docker 로드맵: DB 하나를 compose로 → 앱까지 붙은 compose → Dockerfile → push, Kubernetes는 서버 두 대가 필요해질 때"
checked: 2026-11-16
article_url: https://jjeongil.tistory.com/3182
---

# Docker 로드맵 — 단계별 실측값, 월 비용 계산, 입문 순서 대조

본문에 쓴 단계별 시간이 어느 글의 어떤 측정에서 왔는지, Kubernetes 비교에 쓴 월 비용을 어떻게 계산했는지, 공개된 입문 순서 두 가지와 이 글의 순서가 어디서 갈리는지를 확인할 수 있게 모았다.

## 파일

| 파일 | 내용 |
|---|---|
| `stage-times.csv` | 단계별 실측 시간과 출처 글 (그림 2의 원수치) |
| `monthly-cost.csv` | 사이드 서버 월 비용과 EKS 컨트롤 플레인 계산값 (그림 3의 원수치) |
| `figures/` | 본문 도식 PNG (단계 흐름, Kubernetes 조건·월 비용) |

## 단계별 실측값

모두 Mac의 Docker Desktop에서 단계마다 따로 잰 값이다. 네 단계를 한 번에 이어서 잰 것이 아니므로 더해서 총시간으로 읽으면 안 된다.

| 단계 | 측정 | 값 | 출처 글 |
|---|---|---|---|
| 설치 | Docker Desktop 설치 → `hello-world` | 7분쯤 | [/3007](https://jjeongil.tistory.com/3007) |
| compose | 첫 `docker compose up`, 첫 기동까지 | 20분 안쪽 (이미지 pull 8분쯤 포함) | [/3034](https://jjeongil.tistory.com/3034) |
| Dockerfile | 연습용 `hello-docker` 첫 빌드 / 소스만 고친 재빌드 | 7.8초 / 1.4초 | [/3554](https://jjeongil.tistory.com/3554), [/3034](https://jjeongil.tistory.com/3034) |
| push | Docker Hub 첫 push / 같은 이미지 재push | 50초 안팎 / 5초 안쪽 | [/3035](https://jjeongil.tistory.com/3035) |

- 빌드 시간은 2026-09-17 기록이다.
- push 시간은 약 128MB 이미지 기준이다(출처 글 참고). 이미지 크기와 회선에 따라 크게 달라진다.
- 첫 compose up 20분은 신규 합류자 두 명의 첫 기동 기준이다. Docker를 쓰기 전에는 같은 셋업에 반나절~하루가 걸렸다.

## 월 비용 계산

| 항목 | 월 비용 | 근거 |
|---|---|---|
| RDS | 15달러 안팎 | 저자 사이드 서버 기준 |
| EC2 t3.small 1대 | 19달러쯤 | 저자 사이드 서버 기준(한 달 내내 켜 둔 경우) |
| 사이드 서버 합계 | 34달러 안팎 | 15 + 19 |
| EKS 컨트롤 플레인 | 73달러쯤 | 0.10달러/시간 × 730시간 = 73달러 |

- 사이드 서버 합계에는 스토리지, 백업, 퍼블릭 IPv4, 데이터 전송이 들어 있지 않다.
- EKS 값은 컨트롤 플레인만이다. 워커 노드(EC2), 로드밸런서, EBS 비용은 별도다.
- EKS 요금은 표준 Kubernetes 버전 지원 기준 시간당 0.10달러다. 확장 지원 기간의 클러스터는 시간당 0.60달러라 같은 계산으로 월 438달러쯤이 된다.
- 요금 확인일: 2026-11-16, [Amazon EKS 요금](https://aws.amazon.com/eks/pricing/).

## EKS 시험 기록 (2026년 9월)

운영이 아니라 동작을 눈으로 확인하려고 두 저녁, 합쳐서 10시간쯤 쓴 시험이다.

- 구성: 관리형 컨트롤 플레인 1개 + 워커 t3.medium 2대
- Pod 하나 삭제 → 새 Pod Running까지 약 1.4초
- replica 3 → 10 확장 완료까지 약 8.6초
- 정리 순서: LoadBalancer 타입 Service 삭제 → `eksctl delete cluster` → 남은 EBS 볼륨·탄력적 IP 확인 → 다음 날 Cost Explorer에서 일 비용 확인
- 비용: 계산상 3~4달러. 끝난 다음 날 Cost Explorer의 일 비용은 0으로 표시됐다.

## 입문 순서 대조

2026-11-16에 확인한 공개 순서 두 가지와 이 글의 순서다.

| 순서 | Docker 공식 입문 과정 | roadmap.sh Docker 로드맵 | 이 글 |
|---|---|---|---|
| 1 | 컨테이너 실행 | Introduction(컨테이너란 무엇인가) | DB 하나를 compose로 |
| 2 | 앱 스택 실행 | Linux Fundamentals(패키지 관리자, 사용자·그룹 권한, 셸 명령, 셸 스크립트) | 앱까지 붙은 compose |
| 3 | 이미지 빌드 | Underlying Technologies | Dockerfile |
| 4 | 이미지 공유 | Installation | push |
| 이후 | — | (이후 항목 계속) | 서버 한 대 → 조건이 생기면 Kubernetes |

- 공식 과정은 남이 만든 이미지를 실행하는 것부터 시작한다는 점에서 이 글과 같은 방향이다.
- roadmap.sh는 Linux 기초를 설치보다 앞에 둔다. 「맨 앞」이 아니라 Introduction 다음이다.
- roadmap.sh 페이지에는 로드맵 소유자(Insight Partners)가 Docker 투자사라는 고지가 있다.

## 출처

- Amazon Web Services, 「Amazon EKS pricing」, https://aws.amazon.com/eks/pricing/
- Docker, 「Get started — Workshop」, https://docs.docker.com/get-started/workshop/
- Docker, 「Docker build cache」, https://docs.docker.com/build/cache/
- Docker, 「docker compose down」, https://docs.docker.com/reference/cli/docker/compose/down/
- Kubernetes, 「Overview」, https://kubernetes.io/docs/concepts/overview/
- roadmap.sh, 「Docker Roadmap」, https://roadmap.sh/docker

## 한계

- 실측값은 한 사람의 Mac 환경과 한 팀의 신규 합류자 두 명이 표본이다. 단계마다 측정 시점과 이미지가 다르다.
- 월 비용은 「안팎」「쯤」 단위의 근사값이고 부가 항목을 뺐다.
- EKS 기록은 짧은 시험이며 운영 부하나 장애 상황을 반영하지 않는다.
