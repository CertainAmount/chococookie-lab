---
title: "보조배터리 기내반입 Wh 계산, 20000mAh 라벨에서 읽을 줄과 2개 한도"
checked: 2026-11-15
article_url: ""
---

# 보조배터리 기내 반입 규정 대조와 Wh 계산 근거

이 노트는 글에서 결론만 남긴 두 가지 근거를 담는다. 하나는 기관·항공사·나라별 보조배터리 규정의 시행일과 출처 등급이고, 다른 하나는 mAh를 Wh로 바꾸는 계산과 잘못 계산했을 때의 오차다.

## 파일

| 파일 | 내용 |
|---|---|
| `notice-comparison.csv` | 기관·항공사·나라별 공지 대조표. 내용, 시행일, 출처 주소, 등급, 확인일 |
| `timeline.csv` | 글의 시행일 타임라인 그림에 쓴 원 날짜. 그림에서 뺀 항목은 `in_figure=no` |
| `wh-conversion.csv` | 5,000~50,000mAh × 셀 전압 3.6·3.7·3.85V 환산표와 100Wh·160Wh 경계 mAh |
| `5v-error.csv` | 5V로 곱했을 때의 과대 계산률, 라벨 검산, 5V 기준 정격 용량을 셀 용량으로 착각했을 때의 과소 계산 |

## 수집 방법과 기준일

- 기준일은 2026-11-15다. 등급은 세 가지로 나눴다.
  - **공식 확인**: 정부·국제기구·항공사·공항의 원문 페이지나 문서에서 내용을 확인했다.
  - **보도만**: 언론 보도로만 확인했다. 해당 기관·항공사 공지는 찾지 못했다.
  - **미확인**: 보도끼리 엇갈리거나, 검색 요약에만 있어 원문을 대조하지 못했다.
- 한진그룹 5개 항공사 항목은 대한항공 뉴스룸 보도자료의 제목과 본문 요지로 확인했다.
- IATA 운영사 지침은 PDF 원문(2026-03-31판) 1~6쪽을 읽었다.
- 하네다 공항 안내는 2026-11-15에 페이지를 열어 화면을 캡처했다.
- 계산은 `Wh = mAh × 셀 전압(V) ÷ 1000`, 경계는 `mAh = Wh ÷ 셀 전압 × 1000`이다. 소수는 반올림하지 않고 계산값 그대로 두었다(경계 mAh만 정수로 반올림).

## 정보가 엇갈리는 지점

| 항목 | 엇갈리는 내용 | 이 노트의 처리 |
|---|---|---|
| 국내 시행일 | 보도마다 4월 1일과 4월 20일로 다르게 적혀 있다 | 국토교통부 정책뉴스(2026-04-08)의 「이달 20일부터」로 4월 20일 확정 |
| 100Wh 이하 개수 | 1월 보도는 "100Wh 이하 5개"(개정 전 규정), 2026-07-24에 올라온 한 개인 정리글은 "100Wh 이하는 개수 제한이 느슨하다", 국토부 발표는 용량과 무관하게 1인당 2개 | 2개. 앞의 두 서술은 개정 전 규정이다 |
| 100~160Wh 취급 | ICAO 개정은 항공사 승인 조건으로 허용, IATA는 2027-01-01 시행 DGR 68판에 이 조항을 넣지 않는다고 안내, 국토부 정책뉴스에는 언급이 없다. 일부 2차 자료는 "금지"로 해석한다 | 국내 취급은 확정하지 않고 "출발 전 항공사 확인"으로 둔다 |
| 2개에 여분 배터리 포함 여부 | IATA 지침은 보조배터리(power bank)와 여분 배터리(spare battery)를 분리하고 2개 제한을 보조배터리에만 둔다. 국토부 문구는 「보조배터리는 1인당 최대 2개」로, 여분 배터리 제외를 따로 적은 국내 문장은 찾지 못했다 | ICAO 기준으로는 포함되지 않는다고 쓰고, 항공사 확인을 덧붙인다 |
| 기기 충전 금지의 강도 | ICAO는 비행 중 보조배터리 재충전은 요구 사항, 보조배터리로 기기를 충전하는 것은 권고로 구분한다. 국토부는 둘 다 금지한다 | 국내 기준은 둘 다 금지. 외항사로 일반화하지 않는다 |
| 선반 보관 금지 시점 | 한진그룹 5개 항공사 1/26 공지에 선반 보관 금지가 있다. 정책브리핑에는 「3월부터 보조배터리 기내 선반 보관 금지」 기사(newsId 148939574)가 있고, 2026-04-08 정책뉴스는 지난해부터 선반 보관 금지 등을 시행해 왔다고 쓴다. 선반 금지는 2025년 3월 정부 대책일 가능성이 있으나 원문 연도를 열어 확인하지 않았다 | 표·그림의 1/26 행은 "기내 사용 금지"로만 표시하고, 2025-03 행은 추가하지 않는다 |
| 이스타항공 시행 시점 | 보도마다 2025년 10월과 2026년 1월 1일로 다르다 | 미확인 |
| 티웨이항공 | 2026년 1월 보도 기준 "검토 중", 이후 상태는 확인하지 못했다 | 미확인 |

## 출처

- 국토교통부 정책뉴스(2026-04-08) — https://www.korea.kr/news/policyNewsView.do?newsId=148962298
- ICAO, New power bank restrictions will safeguard international aviation (2026-03-27) — https://www.icao.int/news/new-power-bank-restrictions-will-safeguard-international-aviation
- IATA, Guidance to Operators — Power Banks (PDF) — https://www.iata.org/contentassets/90f8038b0eea42069554b2f4530f49ea/guidance-to-operators---power-banks.pdf
- 대한항공 뉴스룸, 한진그룹 소속 5개 항공사 보조배터리 기내 사용 전면 금지 시행(2026-01-23) — https://news.koreanair.com/%ED%95%9C%EC%A7%84%EA%B7%B8%EB%A3%B9-%EC%86%8C%EC%86%8D-5%EA%B0%9C-%ED%95%AD%EA%B3%B5%EC%82%AC-%EC%98%A4%EB%8A%94-26%EC%9D%BC%EB%B6%80%ED%84%B0-%EB%B3%B4%EC%A1%B0%EB%B0%B0%ED%84%B0%EB%A6%AC/
- 에어프레미아 공지 684 — https://www.airpremia.com/a/ko/customer/notice/684
- 도쿄 하네다 공항, 모바일 배터리 등의 항공기 내 반입(2026년 4월 24일 이후) — https://tokyo-haneda.com/ko/information/2026/detail_00022.html
- JNTO 한국어 안내 — https://www.japan.travel/ko/kr/topic/2026nyeon-4weol-24il-jst-buteo-sihaengdoeneun-ilbon-ginae-banib-bojobaeteori-gyujeong/
- 디지털데일리, 제주항공 기내 보조배터리 사용 금지 — https://www.ddaily.co.kr/page/view/2026012111412097148
- China Daily, Uncertified power banks banned on flights (2025-07-03) — https://govt.chinadaily.com.cn/s/202507/03/WS68663351498edec913cdd2f1/uncertified-power-banks-banned-on-flights.html
- UK CAA, Changes to rules on the carriage of lithium cells/batteries and power banks — https://caa.co.uk/commercial-industry/airlines/dangerous-goods/changes-to-rules-on-the-carriage-of-lithium-cellsbatteries-and-power-banks
- 샤오미 33W Power Bank 10000 사양 — https://www.mi.com/global/product/xiaomi-33w-power-bank-10000-integrated-cable/specs/

## 한계

- 제주항공·중국 항목은 언론 보도로만 확인했다. 싱가포르·대만·이스타·티웨이는 시행일이나 상태를 원문으로 대조하지 못했다.
- 한진그룹 5개 항공사 공지는 공식 보도자료의 제목과 요지로 확인했고, 세부 문구 전체를 대조하지는 않았다.
- 환산표의 셀 전압은 흔히 쓰이는 세 값(3.6·3.7·3.85V)만 넣었다. 실제 제품의 Wh는 라벨 표기를 우선한다.
- 라벨 검산값(앤커 737 24000mAh·86.4Wh·3.6V, 맥고 A1664 10000mAh·37Wh)은 글쓴이가 가진 실물 라벨 값이다.
- 규정은 2027-01-01 IATA DGR 68판 시행 전후로 다시 바뀔 수 있다.
