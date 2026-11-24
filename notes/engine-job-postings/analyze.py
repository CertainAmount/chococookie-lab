"""postings-*.csv를 읽어 개발 직무 공고의 자격증 언급을 분류·집계한다.

사용: python3 analyze.py postings-YYYY-MM-DD.csv
- 분석 대상: 고용24 화면에서 공고 본문을 읽을 수 있는 공고(본문 1,500자 이상)
- 개발 직무: 고용24 「모집 직종」이 소프트웨어·웹·앱 개발 직종인 공고(직접 공고), 또는 연계 공고는 제목 기준
- 결과: summary-YYYY-MM-DD.csv
"""
import csv, re, sys, collections

CERTS = {"정보처리기사": r"정보\s*처리\s*기사|정처기", "정보처리산업기사": r"정보\s*처리\s*산업\s*기사",
         "SQLD": r"SQLD|SQL\s*개발자", "리눅스마스터": r"리눅스\s*마스터", "정보보안기사": r"정보\s*보안\s*기사"}
DEV_JOB = r"소프트웨어\s*(개발자|프로그래머)|웹\s*개발자|애플리케이션\s*프로그래머|프로그래밍\s*언어\s*전문가|컴퓨터\s*시스템\s*및\s*소프트웨어|데이터베이스|IT개발|개발자|프로그래머|엔지니어"
NOT_DEV_JOB = r"강사|디자이너|사무|하드웨어|전자|전기|로봇|기계|조립|사회복지|상담|입력원|영업"
DEV_TITLE = r"백엔드|back[\s-]?end|서버|웹\s*개발|자바|java|spring|스프링|풀스택|full[\s-]?stack|소프트웨어\s*개발|SW\s*개발|S/W|개발자|프로그래머|engineer|엔지니어"


def lic_class(lic, cert_re):
    """자격 면허 칸: '필수 X 우대 Y 기타 ...' 형식."""
    parts = re.findall(r"(필수|우대|기타)\s+(.*?)(?=\s+(?:필수|우대|기타)\s+|$)", lic)
    for kind, name in parts:
        if re.search(cert_re, name):
            return {"필수": "필수", "우대": "우대(자격 칸)", "기타": "우대(자격 칸 기타)"}[kind]
    return ""


def classify(r, cert, cert_re):
    c = lic_class(r["license_field"], cert_re)
    if c:
        return c
    blob = " ".join([r["pref_field"], r["etc_pref"], r["cert_context"] if cert == "정보처리기사" else ""])
    if r.get("has_" + cert) == "1" or re.search(cert_re, blob):
        return "본문 언급"
    return "언급 없음"


def main(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    date = rows[0]["collected"] if rows else ""
    readable = [r for r in rows if int(r["body_len"] or 0) >= 1500 and not r.get("error")]
    def is_dev(r):
        if r["source"] == "고용24 직접":
            return bool(re.search(DEV_JOB, r["job_types"])) and not re.search(NOT_DEV_JOB, r["job_types"].split("관련 직종")[0])
        return bool(re.search(DEV_TITLE, r["title"], re.I))
    dev = [r for r in readable if is_dev(r)]
    out = []
    print(f"수집 {len(rows)} / 본문 읽힘 {len(readable)} / 개발 직무 {len(dev)}")
    groups = collections.OrderedDict()
    groups["고용24 직접"] = [r for r in dev if r["source"] == "고용24 직접"]
    groups["연계(본문 있음)"] = [r for r in dev if r["source"] != "고용24 직접"]
    groups["전체"] = dev
    for g, rs in groups.items():
        for cert, cre in CERTS.items():
            cnt = collections.Counter(classify(r, cert, cre) for r in rs)
            n = len(rs)
            any_ = n - cnt["언급 없음"]
            out.append(dict(date=date, group=g, cert=cert, n=n, mentioned=any_,
                            pct=round(any_ / n * 100, 1) if n else "", **{k: cnt[k] for k in
                            ["필수", "우대(자격 칸)", "우대(자격 칸 기타)", "본문 언급"]}))
            print(f"{g:10s} {cert:8s} n={n:3d} 언급 {any_:3d} ({any_/n*100 if n else 0:.1f}%) {dict(cnt)}")
    by_src = collections.Counter(r["source"] for r in dev)
    print("개발 직무 출처:", dict(by_src))
    lic_any = sum(1 for r in groups["고용24 직접"] if r["license_field"] and r["license_field"] != "관계없음")
    print(f"고용24 직접 개발 공고 중 자격 면허 칸에 무엇이든 적은 공고: {lic_any}/{len(groups['고용24 직접'])}")
    with open(path.replace("postings-", "summary-"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)


if __name__ == "__main__":
    main(sys.argv[1])
