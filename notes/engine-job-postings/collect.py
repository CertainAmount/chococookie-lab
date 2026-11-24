"""고용24 채용정보에서 개발 신입 공고를 모아 자격증 언급을 분류한다.

사용: python3 collect.py --out DIR [--delay 1.5] [--max-detail 600]
- 고용24 공개 검색·상세 화면만 읽는다(로그인 없음, robots.txt 허용 경로).
- 요청 사이 간격을 둔다. 채용 담당자 연락처 등 개인정보는 저장하지 않는다.
- 결과: postings-YYYY-MM-DD.csv (공고 1건 1행), 기준일을 붙여 쌓는다.
"""
import argparse, csv, datetime, html, http.cookiejar, re, sys, time, urllib.parse, urllib.request

BASE = "https://www.work24.go.kr"
LIST = "/wk/a/b/1200/retriveDtlEmpSrchList.do"
UA = {"User-Agent": "Mozilla/5.0 (chococookie-lab research; low-rate)"}
KEYWORDS = ["백엔드", "서버 개발", "웹개발", "웹 개발", "웹프로그래머", "자바", "Java", "스프링", "Spring",
            "개발자", "프로그래머", "소프트웨어 개발", "전산"]
CAREERS = ["N", "Z"]  # 신입, 관계없음
SOURCE_GROUP = {"VALIDATION": "고용24 직접", "ALI": "공공(알리오)", "GOJ": "공공(나라일터)",
                "CLE": "공공(클린아이)", "OEW": "민간(공채속보)"}
CERT = {
    "정보처리기사": r"정보\s*처리\s*기사|정처기",
    "정보처리산업기사": r"정보\s*처리\s*산업\s*기사",
    "정보처리기능사": r"정보\s*처리\s*기능사",
    "SQLD": r"SQLD|SQL\s*개발자",
    "리눅스마스터": r"리눅스\s*마스터",
    "정보보안기사": r"정보\s*보안\s*기사",
    "AWS 자격": r"AWS\s*(자격|인증|SAA|Certified)",
    "관련 자격증(이름 없음)": r"관련\s*자격(증)?\s*(소지|보유)?\s*(자\s*)?우대",
}
BACKEND = r"백엔드|back[\s-]?end|서버|웹\s*개발|웹\s*프로그래|자바|java|spring|스프링|php|node|python|파이썬|django|풀스택|full[\s-]?stack|api|전산|소프트웨어\s*개발|응용\s*소프트웨어|si\b|솔루션\s*개발|프로그래머|개발자"
EXCLUDE = r"하드웨어|회로|기구|설비|건축|토목|전기기사|간호|요양|생산직|영업|디자이너|퍼블리셔|게임\s*그래픽|임베디드|펌웨어|반도체"

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch(path, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    req = urllib.request.Request(BASE + path, data=body, headers=UA)
    for i in range(3):
        try:
            return op.open(req, timeout=40).read().decode("utf-8", "ignore")
        except Exception as e:  # 일시 오류만 재시도
            if i == 2:
                raise
            time.sleep(5)


def text(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>|<caption.*?</caption>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(re.sub(r"\s+", " ", t)).replace("\xa0", " ")


def search(kw, career, delay):
    rows, page = {}, 1
    while True:
        t = fetch(LIST, dict(srcKeyword=kw, siteClcd="all", careerTypes=career, resultCnt="50",
                             pageIndex=str(page), currentPageNo=str(page), sortField="DATE", sortOrderBy="DESC"))
        tot = re.findall(r'txt_total">([\d,]+)', t)
        found = 0
        for m in re.finditer(r'href="(/wk/a/b/1500/empDetailAuthView\.do\?wantedAuthNo=([A-Za-z0-9]+)&(?:amp;)?infoTypeCd=(\w+)&(?:amp;)?infoTypeGroup=(\w+))"', t):
            url, no, cd, grp = m.groups()
            if no not in rows:
                rows[no] = dict(wanted_no=no, info_type=cd, info_group=grp, url=BASE + url.replace("&amp;", "&"))
                found += 1
        for v, cd, comp, title in re.findall(r'value="([A-Za-z0-9]+)\|(\w+)\|([^|"]*)\|([^"]*)"', t):
            if v in rows:
                rows[v].update(company=html.unescape(comp).strip(), title=html.unescape(title).strip())
        total = int(tot[0].replace(",", "")) if tot else 0
        time.sleep(delay)
        if found == 0 or page * 50 >= total or page >= 10:
            return rows, total
        page += 1


def field(x, label, stop):
    m = re.search(re.escape(label) + r"\s+(.{0,400}?)\s+(?:" + stop + ")", x)
    return m.group(1).strip() if m else ""


def detail(row):
    t = fetch(row["url"].replace(BASE, ""))
    x = text(t)
    i = x.find("모집요강")
    body = x[i:] if i >= 0 else x
    j = body.find("채용 담당자")  # 담당자 정보 앞에서 자른다(개인정보 제외)
    body = body[:j] if j > 0 else body
    body = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|0\d{1,2}[-) .]?\d{3,4}[- .]?\d{4}", "[연락처 삭제]", body)
    row["job_types"] = field(body, "모집 직종", "모집 인원|관련 직종|경력")[:200]
    row["career"] = field(body, " 경력", "학력")[:80]
    row["pref_field"] = field(body, "우대조건", "기타 우대사항|근무조건|직무내용|복리후생|전형방법")[:300]
    row["etc_pref"] = field(body, "기타 우대사항", "기타사항|고용허가제|복리후생|전형방법|근무조건")[:300]
    row["license_field"] = field(body, "자격 면허", "근무조건|우대사항|복리후생")[:300]
    row["company_type"] = field(x, "기업규모", "업종|대표자|근로자")[:60]
    hits = {k: bool(re.search(p, body, re.I)) for k, p in CERT.items()}
    row.update({"has_" + k: int(v) for k, v in hits.items()})
    row["cert_context"] = ""
    m = re.search(r".{0,60}(" + CERT["정보처리기사"] + r").{0,60}", body)
    if m:
        row["cert_context"] = m.group(0)
    row["mandatory"] = int(bool(re.search(CERT["정보처리기사"], row["license_field"])) or
                           bool(m and re.search(r"필수|소지자\s*(에\s*한|만)|자격\s*요건", m.group(0))))
    row["bonus"] = int(bool(m and re.search(r"가점|가산", m.group(0))))
    row["body_len"] = len(body)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--max-detail", type=int, default=600)
    a = ap.parse_args()
    today = datetime.date.today().isoformat()
    fetch("/wk/a/b/1200/retriveDtlEmpSrchList.do")
    allrows, totals = {}, []
    for kw in KEYWORDS:
        for c in CAREERS:
            rows, total = search(kw, c, a.delay)
            totals.append((kw, c, total, len(rows)))
            for k, v in rows.items():
                v.setdefault("keywords", set()).add(kw)
                allrows.setdefault(k, v)["keywords"] |= v["keywords"]
            print(f"검색 {kw}/{c}: 총 {total}, 수집 {len(rows)}", file=sys.stderr)
    specific = {"백엔드", "서버 개발", "웹개발", "웹 개발", "웹프로그래머", "Java", "스프링", "Spring"}
    cand = [r for r in allrows.values()
            if not re.search(EXCLUDE, r.get("title", ""))
            and (r["keywords"] & specific or re.search(BACKEND, r.get("title", ""), re.I))]
    print(f"목록 {len(allrows)}건, 개발 직무 제목 {len(cand)}건", file=sys.stderr)
    out = []
    for n, r in enumerate(cand[: a.max_detail], 1):
        try:
            out.append(detail(r))
        except Exception as e:
            r["error"] = str(e)[:80]
            out.append(r)
        if n % 25 == 0:
            print(f"상세 {n}/{len(cand)}", file=sys.stderr)
        time.sleep(a.delay)
    for r in out:
        r["keywords"] = "|".join(sorted(r["keywords"]))
        r["source"] = SOURCE_GROUP.get(r["info_type"], "민간 연계(" + r["info_type"] + ")")
        r["collected"] = today
    cols = ["collected", "wanted_no", "source", "info_type", "company", "title", "keywords", "job_types", "career",
            "company_type", "pref_field", "etc_pref", "license_field"] + ["has_" + k for k in CERT] + \
           ["mandatory", "bonus", "cert_context", "body_len", "url", "error"]
    with open(f"{a.out}/postings-{today}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    with open(f"{a.out}/search-totals-{today}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "career", "total", "collected_rows"])
        w.writerows(totals)
    print(f"저장 {len(out)}건", file=sys.stderr)


if __name__ == "__main__":
    main()
