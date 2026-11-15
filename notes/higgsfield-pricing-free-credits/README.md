---
title: "힉스필드 요금제·무료 크레딧, Seedance 2.0 영상은 어느 플랜부터인가 — Ultra 한 달 3,000크레딧 써 보니"
checked: 2026-11-15
article_url:
---

# 힉스필드 요금제·크레딧 계산 노트

글에 쓴 힉스필드 플랜 가격·모델 단가가 어느 공식 문서의 어느 날짜 값인지, 플랜별 8초 shot 수와 저자의 2026년 9월 사용량을 어떤 계산으로 냈는지 확인하는 노트다. 글마다 가격이 다른 이유를 출처·기준일별로 대조한 표도 함께 둔다.

## 파일

| 파일 | 내용 |
|---|---|
| `official-pricing-snapshot.csv` | 공식 블로그·Help center의 플랜 가격·월 크레딧·동시 생성 수·모델별 단가·크레딧 규칙 스냅샷(본문 표보다 넓게, Team·Scale·Seedance Fast·Mini 포함) |
| `source-comparison.csv` | 기준일별 수치 대조: 공식(10/24·10/25) vs 국내 정리 글(8/11·10/25) vs 3자 자료 — 플랜 가격·크레딧, 무료 크레딧 주장 |
| `shot-count-by-plan.csv` | 플랜 × 해상도별 Seedance 2.0 8초 shot 수 계산(그림 3 원수치) |
| `author-generation-range.csv` | 저자 9월 사용량 재구성 추정 범위(그림 3 주황 띠·그림 4·5 원수치) |
| `figures/` | 본문 도식·캡처 PNG(스크립트가 올림) |

## 수집 방법과 기준일

- 플랜 가격·모델 단가: 힉스필드 공식 블로그 「Pricing Explained」(게시 2026-10-24)를 2026-11-15에 원문 대조했다. 공개 가격표 화면은 같은 날 캡처했다(한국어 자동 번역 화면).
- 8초 720p 단가와 Starter의 Seedance 2.0 범위: 공식 블로그 「Seedance 2.0 pricing 2026」(2026-06-24 게시, 2026-10-25 수정)을 2026-11-15에 확인했다.
- 크레딧 규칙(MCP 차감, 환불, 해지): Help center 문서를 2026-11-15에 조회했다. 해지 문서는 검색 스니펫 기준이다.
- **가격 페이지 렌더링 실패 기록**: `higgsfield.ai/pricing`은 2026-11-15 단순 요청에서 이미지 카드만 돌아왔고, 헤드리스 브라우저 렌더링에서도 HTTP 200에 본문 247자(내비게이션)만 나오고 가격은 보이지 않았다. 로그인·지역 기반 동적 로딩으로 보인다. 그래서 가격 기준을 공식 블로그로 잡았다.

## shot 계산 과정

1. 공식 단가는 5초 기준이다: Seedance 2.0 720p 30, 1080p 60.
2. 8초는 초 비례(× 8/5 = × 1.6)로 계산했다: 720p 48, 1080p 96.
   - 720p 48은 「Seedance 2.0 pricing 2026」의 8초 720p 값과 같다(공식 확인).
   - 1080p 96은 공식 8초 값이 없어 같은 비례를 적용한 계산값이다. 저자 기억("약 100")과 맞는다.
3. 플랜별 shot 수 = 월 크레딧 ÷ 8초 단가, 소수점 이하 버림.
   - Starter 200 → 720p 4.17 → 4개, 1080p 2.08 → 2개 (Seedance 2.0 표준을 쓸 수 없어 실제로는 해당 없음)
   - Plus 1,000 → 720p 20.83 → 20개, 1080p 10.42 → 10개
   - Ultra 3,000 → 720p 62.50 → 62개, 1080p 31.25 → 31개

## 9월 사용량 재구성 추정

- 처음 생성 20개 + 재생성 25~35번 = 생성 45~55번.
- 전부 720p 단가 48로 잡으면 45 × 48 = 2,160, 55 × 48 = 2,640크레딧.
- Ultra 3,000에서 빼면 360~840크레딧이 남는다. 저자는 최종 컷을 1080p로 다시 뽑았으므로 이 몫의 상당 부분이 1080p 생성에 쓰였다고 본다.
- 끝 잔액은 "몇십~이백대"라는 저자 범위값이다. 1080p 최종 컷 수를 모르므로 720p·1080p로 나눠 끝 잔액과 정확히 맞추지는 않는다.

## 출처

- Higgsfield, 「Pricing Explained」, https://higgsfield.ai/blog/higgsfield-pricing-explained
- Higgsfield, 「Seedance 2.0 pricing 2026」, https://higgsfield.ai/blog/seedance-2-0-pricing-2026
- Higgsfield Help center, 「What is Higgsfield MCP」, https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp
- Higgsfield Help center, 「Can I get a refund for a subscription I never used」, https://higgsfield.ai/creator-hub/help-center/refunds-and-cancellations/can-i-get-a-refund-for-a-subscription-i-never-used
- Higgsfield Help center, 「How do I cancel my subscription」, https://higgsfield.ai/creator-hub/help-center/refunds-and-cancellations/how-do-i-cancel-my-subscription
- Higgsfield, 「Unlimited MCP」(2026-07-28), https://higgsfield.ai/blog/unlimited-mcp
- 국가법령정보센터, 부가가치세법 제53조의2, https://www.law.go.kr/법령/부가가치세법
- 대조표의 국내 정리 글·3자 자료는 수치 비교용이며 글 본문에서 인용하지 않았다.

## 한계

- 저자 사용량(재생성 횟수, 끝 잔액, 카드 청구액)은 사용 내역 화면 기록이 아니라 기억에 기반한 범위값이다.
- 1080p 8초 96크레딧은 계산값이다. 「Pricing Explained」 본문에는 "720p에서 1080p로 가면 가격이 거의 세 배"라는 문장이 있지만 같은 글의 단가표는 30 → 60(두 배)이다. 계산은 단가표를 따랐다.
- Starter에서 Seedance 2.0 표준이 막혀 있다는 판단은 공식 블로그 두 편(Starter "선택된 모델", 표준은 $49 플랜으로 사용)과 3자 자료가 같은 방향이라 확정으로 처리했다. 이를 한 문장으로 못 박은 공식 문구는 없다.
- 저자가 결제한 2026년 9월 당시의 공식 가격 스냅샷은 없다. 6월 게시 공식 글(10/25 수정본)도 Ultra $129·3,000을 적고 있어 모순은 없다.
- 무료 크레딧 수치(125 일회성 / 0 / 매일 소량)는 3자 자료마다 다르고 공식 문서에는 "Free 플랜 월 크레딧 없음"만 있다.
