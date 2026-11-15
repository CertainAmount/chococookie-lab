"""블로그 리눅스 검색어를 리눅스마스터 출제기준 영역별로 집계한다.

입력: Google Search Console 검색어×페이지 90일 export를 다음 형태로 바꾼 JSON
  {"queries": {"검색어": [{"page": URL, "impressions": int, "clicks": int, ...}, ...]}}
출력: 영역별 집계 CSV(영역, 출제기준 대응, 검색어 수, 노출, 클릭)와 합계 한 줄.
검색어 문자열이나 검색어별 수치는 내보내지 않는다.

사용: python3 classify_linux_queries.py --input gsc-queries.json --output areas.csv
"""
import argparse
import collections
import csv
import json
import re

# 리눅스 관련 검색어 필터. PHP 버전 검색어는 리눅스 명령으로 버전을 확인하는 글로
# 들어오는 검색어라 의도적으로 포함했다(README 「한계」 참고).
LINUX = re.compile(
    r'리눅스|linux|우분투|ubuntu|centos|rocky|debian|데비안|레드햇|rhel|redhat|\bvi\b|\bvim\b|\bnano\b|'
    r'chmod|chown|crontab|\bcron\b|systemctl|\bapt\b|apt-get|\byum\b|\bdnf\b|\bsudo\b|passwd|\bgrep\b|'
    r'\btar\b|\bssh\b|\bdf\b|\bdu\b|\bmount\b|fdisk|\bps\b|\bkill\b|\bhtop\b|\bbash\b|쉘|셸|\bshell\b|'
    r'useradd|usermod|userdel|\bls\b|\bcp\b|\bmv\b|\brm\b|mkdir|rmdir|\bfind\b|\bwget\b|ifconfig|netstat|'
    r'firewall|iptables|\bufw\b|selinux|uname|lsblk|journalctl|\bnetcat\b|pgrep|심볼릭|grub|xrdp|\bnfs\b|'
    r'php 버전|php version|php버전',
    re.I,
)

# 영역 규칙. 위에서부터 처음 맞은 영역 하나에만 넣는다. 순서를 바꾸면 결과가 바뀐다.
AREAS = [
    ('부팅·재부팅', '설치 > 부트 매니저',
     r'grub|부팅|\bboot\b|reboot|재부팅|usb'),
    ('사용자·계정·비밀번호', '기본 명령어 > 사용자 생성 및 계정 관리',
     r'비밀번호|패스워드|비번|유저|passwd|password|useradd|adduser|usermod|userdel|사용자|계정|user|root|sudo|su '),
    ('에디터(vi·vim·nano)', '에디터',
     r'\bvi\b|vim|nano|에디터|editor|저장하고|빠져나|나가기|insert'),
    ('파일·디렉터리·압축', '기본 명령어 > 디렉터리 및 파일',
     r'폴더|디렉토리|디렉터리|파일|\brm\b|mkdir|rmdir|\bcp\b|\bmv\b|touch|\bfind\b|\bls\b|복사|이동|압축|\btar\b|\bzip\b|심볼릭|\bln\b|\bless\b|\btr\b'),
    ('권한·소유자', '권한 및 그룹 설정',
     r'chmod|chown|권한|permission|그룹|group'),
    ('버전·메모리 등 시스템 정보', '기타 명령어, 프로세스 유틸리티',
     r'메모리|램 |memory|\bcpu\b|\bfree\b|사양|정보 확인|uname|커널|kernel|버전|version'),
    ('디스크·마운트·파티션', '파일 시스템 관리, 설치 > 파티션',
     r'디스크|\biso\b|disk|\bdf\b|\bdu\b|mount|마운트|fdisk|파티션|partition|lsblk|swap|스왑|fstab'),
    ('프로세스·서비스', '프로세스 관리',
     r'프로세스|process|\bps\b|\bkill\b|\btop\b|htop|systemctl|서비스|\bservice\b|\bcron\b|crontab|nohup|백그라운드|데몬|pgrep'),
    ('패키지·SW 설치·삭제', '소프트웨어 설치',
     r'\bapt\b|\byum\b|\bdnf\b|\brpm\b|dpkg|설치|install|업데이트|upgrade|update|패키지|package|삭제'),
    ('셸·환경변수', 'Shell > 환경 설정',
     r'\bbash\b|쉘|셸|\bshell\b|환경변수|\bpath\b|alias|export|bashrc|profile|스크립트|history'),
    ('네트워크·SSH·방화벽', '인터넷 활용 > 인터넷 서비스 설정',
     r'\bssh\b|\bip\b|ifconfig|네트워크|network|포트|\bport\b|netstat|방화벽|firewall|iptables|\bufw\b|\bscp\b|wget|curl|\bdns\b|hostname|nginx|apache|httpd|samba|\bnfs\b|\bftp\b'),
    ('X 윈도·원격 데스크톱', 'X 윈도',
     r'xrdp|vnc|gui|x window|x11|gnome|kde|데스크톱|desktop'),
    ('로그·텍스트 처리', '기타 명령어',
     r'로그|\blog\b|\bgrep\b|\btail\b|\bhead\b|\bcat\b|\bsed\b|\bawk\b|\bwc\b|netcat'),
]
UNCLASSIFIED = '미분류'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--input', required=True, help='GSC 검색어×페이지 JSON')
    ap.add_argument('--output', default='areas.csv', help='집계 CSV 경로')
    args = ap.parse_args()

    with open(args.input, encoding='utf-8') as f:
        queries = json.load(f)['queries']

    rules = [(name, exam, re.compile(rx, re.I)) for name, exam, rx in AREAS]
    agg = collections.OrderedDict(
        (name, {'exam': exam, 'q': 0, 'imp': 0, 'clk': 0}) for name, exam, _ in rules
    )
    agg[UNCLASSIFIED] = {'exam': '', 'q': 0, 'imp': 0, 'clk': 0}
    total = {'q': 0, 'imp': 0, 'clk': 0}

    for q, rows in queries.items():
        text = q + ' '
        if not LINUX.search(text):
            continue
        imp = sum(r['impressions'] for r in rows)
        clk = sum(r['clicks'] for r in rows)
        area = next((name for name, _, rx in rules if rx.search(text)), UNCLASSIFIED)
        for g in (agg[area], total):
            g['q'] += 1
            g['imp'] += imp
            g['clk'] += clk

    with open(args.output, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['area', 'exam_item', 'queries', 'impressions', 'clicks'])
        classified = [kv for kv in agg.items() if kv[0] != UNCLASSIFIED]
        for name, g in sorted(classified, key=lambda kv: -kv[1]['clk']) + [(UNCLASSIFIED, agg[UNCLASSIFIED])]:
            w.writerow([name, g['exam'], g['q'], g['imp'], g['clk']])
        w.writerow(['합계', '', total['q'], total['imp'], total['clk']])


if __name__ == '__main__':
    main()
