---
title: "Freeze-Omni vs STT·LLM·TTS cascade 음성 대화 지연: 실사용 약 1.2초, 내 cascade는 2.0~3.5초"
checked: 2026-11-17
article_url:
---

# Freeze-Omni 지연 분해·Spoken QA·원문 대조 노트

글에서 결론만 남긴 숫자의 계산 과정과 원값을 모았다. Freeze-Omni 쪽은 모두 arXiv 2411.00774 v5 원문 값이고, cascade·Gemini Live API 쪽은 저자 환경의 범위값이다.

## 파일

| 파일 | 내용 |
|---|---|
| `README.md` | 지연 구간 분해 계산표, Spoken QA 원값, 발표 요약 원고와 원문 대조표, 구조 수치 원표 |
| `latency-figure.csv` | 지연 막대 그림(figure-3)의 원수치. 구성·구간별 하한·상한·대표값과 값 종류(논문/계산/저자 범위) |
| `figures/` | 글에 쓴 도식 PNG(지연 막대, 모듈 구조도, 듀플렉스 상태·에코 흐름) |

## 1. 지연 구간 분해 계산표

기준점: 사용자 발화 종료 → 첫 오디오.

| 구성 | 구간 | 값 | 종류 |
|---|---|---|---|
| Freeze-Omni | 비통계 지연: 인코더가 청크 1~2개를 기다리는 시간 | 160~320ms | 논문 |
| Freeze-Omni | 통계 지연: 상태 판정 → 첫 PCM 청크 | 평균 745ms, 중앙값 753ms, P90 1,020ms | 논문 |
| Freeze-Omni | 네트워크 | 200~300ms | 논문 |
| Freeze-Omni | 세 구간 합(평균 745ms 사용) | 160+745+200 = 1,105ms ~ 320+745+300 = 1,365ms | 계산 |
| Freeze-Omni | 실사용 평균 | "about 1.2 seconds" | 논문 |
| 저자 cascade | 전체: 발화 종료(VAD 판단) → 첫 오디오 청크 수신 | 2.0~3.5초 | 저자 로그 범위 |
| 저자 cascade | STT 확정 / LLM 첫 응답 / TTS 첫 오디오 | 500~900ms / 700ms~1.5초 / 500~900ms | 저자 로그 범위 |
| Gemini Live API | 전체 | 1초 안팎 | 저자 사용감(2026-09) |

계산 메모

- 1,105~1,365ms는 하한끼리, 상한끼리 더한 범위다. 745ms가 평균이라 엄밀한 상·하한은 아니고, 논문의 "about 1.2 seconds"가 이 범위 안에 든다는 확인용이다.
- 저자 cascade의 단계별 값은 같은 trace 로그의 타임스탬프 차이를 훑어 본 범위다. 전체와 정의가 다르다. VAD가 끝을 판정하기 전의 무음 대기, 단계 사이 네트워크·큐 대기는 단계 값에 없고, 한 턴에서 세 단계가 모두 상단에 걸리는 경우는 드물다. 그래서 단계 범위를 더해 전체를 만들지 않았다.
- 저자 값은 첫 오디오 청크를 "받은" 시점이라 재생 버퍼만큼 실제 소리는 더 늦다. 논문 값과 저자 값은 측정 환경이 달라 같은 실험 조건의 비교가 아니다.

## 2. Spoken QA 원값 (arXiv 2411.00774 v5)

| 항목(원문 표기) | Qwen2-7B-Instruct, 텍스트 질문 | Freeze-Omni, 음성 질문 | 차이 |
|---|---|---|---|
| Web Q. | 45.13 | 44.73 | -0.40 |
| LlaMA Q. | 77.67 | 72 | -5.67 |
| Audio Trivia QA | 63.93 | 53.88 | -10.05 |

- 차이는 음성 값 − 텍스트 값으로 계산했다.
- PMLR v267 게재본 PDF와의 수치 대조는 하지 못했다. 위 값은 arXiv v5 기준이다.

## 3. 발표 요약 원고와 원문 대조표

논문 읽기 모임 발표 요약 원고의 표현을 원문과 맞춰 본 결과다. 글에서는 1.2초의 의미와 상태 정의 두 곳만 다뤘다.

| 항목 | 요약 원고 표현 | 원문(arXiv v5) |
|---|---|---|
| 1.2초의 의미 | 1.2초보다 훨씬 짧다 | 네트워크까지 넣은 실사용 평균이 약 1.2초. 모델 안 통계 지연 평균은 745ms |
| 지연 구분 | 자동 측정 / 수동 측정 | 통계 지연(상태 판정 → 첫 PCM 청크)과 비통계 지연(인코더 청크 대기 160~320ms), 그리고 네트워크 200~300ms |
| 듀플렉스 상태 1 | 생성 시작 | 사용자가 끼어들었고 LLM이 새 생성을 시작 |
| 듀플렉스 상태 2 | 생성 종료 | 사용자 발화가 끝났고 끼어들 필요 없음 |
| 여러 모델 서버 | 끼어들기 지연을 줄이는 장치 | Model as a Server: 청크가 올 때마다 놀고 있는 인스턴스에 배정, 사용자별 kv-cache·CNN cache를 서버가 보관 |
| prefix 디코더 효과 | 오류와 분산 감소 | CER 감소만 보고(top-1 5.27→3.9, pre-network 포함 3.11→2.19) |
| Audio Trivia QA | 53 | 53.88 |
| 학습 데이터 언어 | 언급 없음 | 11만 시간, 중국어·영어 내부 데이터 |
| 라이선스 | 언급 없음 | GitHub License.txt는 학술·연구·교육 목적 한정, Hugging Face 카드 태그는 apache-2.0 |
| 공개 범위 | 언급 없음 | 2024-11-26 추론 코드·서버 데모·가중치 공개, README에 학습 코드 언급 없음 |

## 4. 구조 수치 원표 (arXiv v5)

| 모듈 | 수치 |
|---|---|
| 음성 인코더 | 4배 다운샘플 합성곱 + Transformer 24층, hidden 1024, 약 350M, 출력 12.5Hz, 1단계 CTC 학습 |
| 어댑터 | 2배 다운샘플 합성곱 |
| 입력 쪽 3단계 데이터 | 1단계 11만 시간(중·영), 3단계 멀티턴 QA 6만 건(moss-003-sft-data에서 추출, 답변은 백본 LLM으로 재생성), 학습 GPU 8장 |
| dynamic chunk(WeNet 방식) | 동적 학습에서 chunk=∞가 chunk=4보다 오류율 낮음. 동적 학습 없이 chunk=4 고정 학습이 동적 학습의 chunk=4보다 나음 |
| 코덱 | TiCodec 개조: 단일 코드북 1024개, 토큰 40Hz, 출력 24kHz |
| 음성 디코더 | NAR·AR 디코더 각 4층, hidden 896, 전체 약 120M. prefix 디코더가 LLM 은닉 상태의 kv-cache를 NAR 디코더에 공급 |

## 수집 방법과 기준일

- 기준일 2026-11-17. 논문 수치는 arXiv HTML v5(2024-12-08)에서 직접 읽었다.
- 라이선스·공개 범위는 GitHub 저장소 README와 License.txt, Hugging Face 모델 카드를 같은 날 확인했다.
- 저자 cascade 값은 2024년 사이드프로젝트(Whisper 계열 STT → GPT 계열 LLM → ElevenLabs TTS)의 trace 로그 범위, Gemini Live API 값은 2026년 9월 파이썬 프로토타입 사용감이다.

## 출처

- Freeze-Omni 논문, arXiv 2411.00774 v5 — https://arxiv.org/html/2411.00774v5
- PMLR v267 게재본(ICML 2025) — https://proceedings.mlr.press/v267/wang25aw.html
- GitHub VITA-MLLM/Freeze-Omni — https://github.com/VITA-MLLM/Freeze-Omni
- Freeze-Omni License.txt — https://github.com/VITA-MLLM/Freeze-Omni/blob/main/License.txt
- Hugging Face VITA-MLLM/Freeze-Omni — https://huggingface.co/VITA-MLLM/Freeze-Omni

## 한계

- Freeze-Omni를 직접 실행해 잰 값은 없다. Freeze-Omni 값은 전부 논문 값이다.
- 저자 cascade 값은 정식 벤치마크가 아니라 로그를 훑어 본 범위, Gemini Live API는 사용감 기준이다. 개별 타임스탬프는 싣지 않았다.
- PMLR 게재본 수치와의 대조는 하지 못했다.
