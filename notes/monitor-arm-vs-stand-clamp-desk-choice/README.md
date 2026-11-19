---
title: "모니터암 vs 모니터 받침대 선택, 30mm 상판인데 보강 프레임 5cm에 걸려 클램프가 안 물렸다"
checked: 2026-11-19
article_url:
---

# 모니터암 vs 모니터 받침대 — 그림 원값과 사양 출처

글에 실은 세 그림(높이·거리 비교, 상판 단면, 하중 범위)의 원수치와, 모니터·암 사양을 어느 공식 문서에서 확인했는지 모은 노트다.

## 파일

| 파일 | 내용 |
|---|---|
| `figure-values.csv` | 그림 1~3에 쓴 값 전체. 값마다 출처 구분(저자 어림값·저자 줄자·계산·제조사 문서)과 비고 |
| `figures/` | 본문 그림 PNG(SVG에서 1600px로 렌더링) |

## 수집 방법과 기준일

- 책상·화면 치수: 저자 집 책상(1400×800, 원목 집성 30mm 상판, 철제 다리)에서 줄자로 잰 어림값. 화면 높이·눈높이는 책상 윗면 기준이다.
- 클램프 아래 판 깊이 약 9cm: 직접 잰 값이 아니라, 2023년 12월 판매처에 보낸 사진과 제품 박스 크기로 가늠한 값이다.
- 제조사 사양: 2026-11-19에 아래 공식 문서와 대조했다.

## 사양 출처 대조

| 항목 | 값 | 출처 | 비고 |
|---|---|---|---|
| Dell U2723QE 무게(스탠드 제외) | 4.48kg | Dell 사용자 가이드 | 암 하중에 넣는 값 |
| Dell U2723QE VESA | 100×100mm | Dell 사용자 가이드 | |
| Ergotron LX 데스크 마운트 하중 | 3.2~11.3kg(7~25lb) | Ergotron LX 사양서 | |
| Ergotron LX 모니터 깊이 주석 | 64mm(2.5") 초과 시 하중 감소 가능 | Ergotron LX 치수 도면(dim2-056) | 커브드·울트라와이드 해당 |
| 하중 여유 권고 | 하한·상한 양쪽 최소 1~2kg | BenQ 지식센터 | 벤더 권고 |
| 상판 모서리 | 약 2.5cm 이상 둥글거나 사선이면 클램프 고정력 저하 가능 | BenQ 지식센터 | 벤더 권고 |
| 벽과의 여유 | 최소 약 5cm | BenQ 지식센터 | 벤더 권고 |

Ergotron 문서에서 찾은 「클램프·그로밋 최대 상판 두께 65mm」는 같은 계열 다른 제품(Sit-Stand) 사양서 표기라 LX 단품 값으로 쓰지 않았다.

## 출처

- Dell, U2723QE Monitor User's Guide — https://dl.dell.com/content/manual12109242-dell-u2723qe-monitor-user-s-guide.pdf?language=en-us
- Ergotron, LX Desk Mount 사양서 — https://media.ergotron.com/reserved/resources/lx-arms-fur-all-ea-orig.pdf
- Ergotron, LX 치수 도면(dim2-056) — https://media.ergotron.com/reserved/resources/dim2-056-orig.pdf
- BenQ, 모니터 암 구매 시 고려사항 10가지 — https://www.benq.com/ko-kr/knowledge-center/knowledge/10-things-to-consider-when-buying-a-monitor-arm.html

## 한계

- 책상·화면 치수는 한 책상, 한 사람의 어림값이다. 화면 높이와 눈높이는 「쯤」 단위로 읽는다.
- 처음 산 저가 암의 하중(2~9kg)과 클램프 범위(10~80mm)는 구매 당시 사양표를 기억한 값이다. 브랜드는 확인되지 않는다.
- 클램프 아래 판 깊이(약 9cm)는 사진·박스로 가늠한 추정값이다. 에르고트론 LX 클램프 아래 판(6~7cm쯤)은 기억값이라 그림과 표에 넣지 않았다.
