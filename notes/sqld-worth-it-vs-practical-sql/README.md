---
title: SQLD 따야 하나, 백엔드 면접관이 서류와 면접에서 본 경계
checked: 2026-11-15
article_url:
---

# SQLD 시험 범위와 실무 SQL 대조 — 연구 노트

SQLD 현행 출제기준 세부항목을 PostgreSQL·MySQL 실무 문법과 항목 단위로 맞춘 대조표, 2026년 회차 일정 원표, 합격률을 쓰는 출처별 차이, 본문 실행계획 화면을 다시 만드는 방법을 모았다.

## 파일

| 파일 | 내용 |
|---|---|
| `syllabus-vs-practice.csv` | 출제기준 세부항목 전체(5개 묶음)와 출제기준 밖 실무 항목 4개. 항목마다 실무 분류(그대로 쓴다 / 문법만 다시 익힌다 / 개념만 겹침 / 시험 밖 / 미분류)와 PostgreSQL·MySQL 문법 |
| `schedule-2026.csv` | 2026년 제60~63회 접수·시험·사전점수 공개·결과 발표일 |
| `pass-rate-sources.csv` | 합격률을 제시하는 출처별 방식, 원출처 표기, 확정·예상 구분 |
| `explain-row-number.sql` | 합성 주문 20만 건 생성, 인덱스 전후 `EXPLAIN ANALYZE` |
| `explain-output.txt` | 위 SQL의 원출력(인덱스 전 블록, 인덱스 후 블록) |

## 수집 방법과 기준일

- **출제기준 대조**: 데이터자격검정 SQLD 안내 페이지의 출제기준 세부항목을 2026-11-15에 열람해 그대로 옮겼다. 실무 분류 열은 필자가 개인 프로젝트(PostgreSQL)와 회사 업무(MySQL, JPA/QueryDSL)에서 쓰는 방식을 기준으로 정한 결론이다. 저장소 쿼리를 도구로 집계한 값이 아니다.
- **일정**: 데이터자격검정 시험일정 페이지를 2026-11-15에 열람했다. 같은 날 기준으로 2027년 회차는 게시되지 않았다.
- **합격률 출처 대조**: 2026-11-15에 SQLD 관련 상위 검색 결과를 열어 합격률 표의 원출처 표기를 기록했다. 공식 SQLD 안내 페이지에는 회차별 합격률을 볼 수 있는 메뉴가 없었다. 본문에는 합격률 숫자를 쓰지 않았다.
- **실행계획 재현**: 아래 절차로 PostgreSQL 18.6에서 실행했다.

### 실행계획 재현 방법

1. PostgreSQL 18 서버를 준비한다. 로컬 `psql`이 있으면 임시 데이터베이스에서 실행하고, 없으면 컨테이너를 쓴다.

   ```
   docker run -d --name sqld-explain --cpus=2 -e POSTGRES_PASSWORD=explain postgres:18
   sleep 5
   docker exec -i sqld-explain psql -X -q -U postgres < explain-row-number.sql
   docker rm -f sqld-explain
   ```

2. `explain-row-number.sql`은 `setseed(0.42)`로 고객 번호 1~20,000에 주문 20만 건(2025년 한 해 안의 무작위 주문 시각)을 만든 뒤 `ANALYZE`한다.
3. 첫 번째 `EXPLAIN (ANALYZE, COSTS OFF, BUFFERS OFF)`는 인덱스 없이 고객별 최근 주문 1건을 `ROW_NUMBER()`로 뽑는 쿼리의 계획이다.
4. `(customer_id, ordered_at DESC)` 인덱스를 만들고 같은 쿼리를 다시 본다. 플래너 설정(`enable_seqscan` 등)은 바꾸지 않았다.

결과 요약(`explain-output.txt`):

| 구분 | 계획 | 정렬 | 실행 시간 |
|---|---|---|---|
| 인덱스 전 | Seq Scan → Sort → WindowAgg(Run Condition) → Subquery Scan | `external merge  Disk: 7448kB` | 124.629 ms |
| 인덱스 후 | Index Scan using orders_customer_recent → WindowAgg → Subquery Scan | 없음 | 105.977 ms |

## 계층 쿼리 순환 재현 (본문 「계층 쿼리는 문법보다 데이터에서 터진다」)

운영에서 조직 코드 계층 `WITH RECURSIVE` 쿼리가 끝나지 않았던 일을, 2026-10-18 로컬 PostgreSQL 18.6에서 합성 데이터로 다시 만든 기록이다. 운영 데이터는 쓰지 않았다.

| 조건 | 결과 |
|---|---|
| 노드 100,000개, 깊이 10의 단일 루트 계층, 가드 없는 `WITH RECURSIVE` | 135ms에 종료 |
| 루트의 부모를 50000번 노드로 바꿔 순환 생성, 가드 없음, `statement_timeout = 10s` | 10초에서 취소 |
| 같은 순환 데이터, `CYCLE` 절 추가 | 333ms에 100,001행 반환, 순환 표시 1건 |

- 시간은 이 환경 한 번의 값이다. 비교할 것은 「끝나느냐」와 「순환을 표시하느냐」다.
- `CYCLE` 절 문법: PostgreSQL 문서 「WITH Queries」의 Cycle Detection 절.

## 출처

- 한국데이터산업진흥원 데이터자격검정, 「SQL 개발자(SQLD)」 — https://www.dataq.or.kr/www/sub/a_04.do
- 한국데이터산업진흥원 데이터자격검정, 「시험일정」 — https://www.dataq.or.kr/www/accept/schedule.do
- MySQL 8.0 Reference Manual, 「Statements That Cause an Implicit Commit」 — https://dev.mysql.com/doc/refman/8.0/en/implicit-commit.html
- MySQL 8.0 Reference Manual, 「Regular Expressions」 — https://dev.mysql.com/doc/refman/8.0/en/regexp.html
- PostgreSQL Documentation, 「WITH Queries」 — https://www.postgresql.org/docs/current/queries-with.html
- PostgreSQL Documentation, 「tablefunc」 — https://www.postgresql.org/docs/current/tablefunc.html

## 한계

- 대조표의 「미분류」 항목(데이터모델의 이해, 엔터티, 속성, 관계, 관계형 데이터베이스 개요, Top N 쿼리)은 필자가 실무 사용 여부를 따로 판단하지 않은 항목이다.
- 실무 분류는 필자 한 사람의 두 환경 기준이다. 다른 DBMS나 조직에서는 달라질 수 있다.
- 합격률: 공식 자료실·공지사항은 열람하지 못했다. 2차 자료의 수치는 어느 자료가 정확히 어떤 회차 값을 쓰는지 서로 맞지 않고, 2025년 수치는 확정치인지 예상치인지가 자료마다 다르다. 정리글의 개별 주소는 기록하지 않았다.
- 실행계획 재현은 합성 데이터이며 실행 시간은 이 환경 한 번의 값이다. 20만 건 전체를 읽는 쿼리라 인덱스 전후 실행 시간 차이는 작다. 확인할 것은 시간보다 Sort가 사라지는 계획 변화다.
