"""
Luca - 남양주 백병원 네이버 주간 키워드 모니터링
매주 자동 실행되어 텔레그램으로 리포트를 전송하는 스크립트
"""
import urllib.request
import urllib.parse
import json
import ssl
import sys
import io
from datetime import datetime, timedelta

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# API 자격 증명
NAVER_SEARCH_CLIENT_ID = "KfgaSIkWNVGJ_YSZcffs"
NAVER_SEARCH_CLIENT_SECRET = "CSYMZPGOdP"
NAVER_DATALAB_CLIENT_ID = "q8Y3EuiGXRYGjemuDFYv"
NAVER_DATALAB_CLIENT_SECRET = "HLddlF0Qc1"

# 모니터링 대상 설정
MAIN_KEYWORD = "남양주 백병원"
COMPETITOR_KEYWORDS = ["남양주 정형외과", "다산 정형외과", "남양주 내과"]
SPECIALTY_KEYWORDS = ["남양주 백병원 건강검진", "남양주 하지정맥"]


def _ssl_context():
    return ssl._create_unverified_context()


def get_trend(keywords, days=7):
    """지정 기간의 데이터랩 트렌드를 조회합니다."""
    end = datetime.now()
    start = end - timedelta(days=days)
    keyword_groups = [{"groupName": k, "keywords": [k]} for k in keywords]
    body = json.dumps({
        "startDate": start.strftime("%Y-%m-%d"),
        "endDate": end.strftime("%Y-%m-%d"),
        "timeUnit": "date",
        "keywordGroups": keyword_groups
    }).encode("utf-8")

    req = urllib.request.Request("https://openapi.naver.com/v1/datalab/search")
    req.add_header("X-Naver-Client-Id", NAVER_DATALAB_CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", NAVER_DATALAB_CLIENT_SECRET)
    req.add_header("Content-Type", "application/json")
    try:
        res = urllib.request.urlopen(req, data=body, context=_ssl_context())
        if res.getcode() == 200:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"트렌드 API 오류: {e}", file=sys.stderr)
    return None


def get_blog_count(keyword, display=5):
    """블로그 검색 결과를 가져옵니다."""
    enc = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/blog?query={enc}&display={display}"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", NAVER_SEARCH_CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", NAVER_SEARCH_CLIENT_SECRET)
    try:
        res = urllib.request.urlopen(req, context=_ssl_context())
        if res.getcode() == 200:
            data = json.loads(res.read().decode("utf-8"))
            return data.get("total", 0), data.get("items", [])
    except Exception as e:
        print(f"블로그 검색 API 오류: {e}", file=sys.stderr)
    return 0, []


def build_report():
    """주간 모니터링 리포트 문자열을 생성합니다."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    
    lines = []
    lines.append(f"📊 *Luca 네이버 주간 키워드 리포트*")
    lines.append(f"🗓 분석일: {date_str} (최근 7일)")
    lines.append("")

    # ── 1. 메인 키워드 트렌드 ──
    lines.append("*1️⃣ 남양주 백병원 검색 추이*")
    main_trend = get_trend([MAIN_KEYWORD], days=7)
    if main_trend and main_trend.get("results"):
        r = main_trend["results"][0]
        data = r.get("data", [])
        if data:
            avg = sum(d["ratio"] for d in data) / len(data)
            peak = max(data, key=lambda x: x["ratio"])
            low = min(data, key=lambda x: x["ratio"])
            lines.append(f"  • 평균 검색지수: *{avg:.1f}*")
            lines.append(f"  • 최고점: {peak['period']} ({peak['ratio']:.0f}점)")
            lines.append(f"  • 최저점: {low['period']} ({low['ratio']:.0f}점)")
            # 상승/하락 트렌드 판단
            if len(data) >= 4:
                first_half = sum(d["ratio"] for d in data[:len(data)//2])
                second_half = sum(d["ratio"] for d in data[len(data)//2:])
                if second_half > first_half * 1.1:
                    lines.append("  📈 추세: *상승 중* ✅")
                elif second_half < first_half * 0.9:
                    lines.append("  📉 추세: *하락 중* ⚠️")
                else:
                    lines.append("  ➡️ 추세: 보합")
        else:
            lines.append("  (이번 주 데이터 없음)")
    else:
        lines.append("  (조회 실패)")
    lines.append("")

    # ── 2. 경쟁 키워드 비교 ──
    lines.append("*2️⃣ 경쟁 키워드 비교*")
    comp_all = [MAIN_KEYWORD] + COMPETITOR_KEYWORDS
    comp_trend = get_trend(comp_all, days=7)
    if comp_trend and comp_trend.get("results"):
        sorted_results = sorted(
            comp_trend["results"],
            key=lambda r: sum(d["ratio"] for d in r.get("data", [])),
            reverse=True
        )
        for i, r in enumerate(sorted_results, 1):
            data = r.get("data", [])
            avg = sum(d["ratio"] for d in data) / len(data) if data else 0
            medal = ["🥇", "🥈", "🥉", "4️⃣"][min(i-1, 3)]
            lines.append(f"  {medal} {r['title']}: *{avg:.1f}점*")
    else:
        lines.append("  (조회 실패)")
    lines.append("")

    # ── 3. 블로그 노출 현황 ──
    lines.append("*3️⃣ 블로그 최신 노출 현황*")
    total, items = get_blog_count(MAIN_KEYWORD, display=3)
    if items:
        lines.append(f"  총 포스팅 수: {total:,}건")
        for item in items[:2]:
            title = item.get("title", "").replace("<b>", "").replace("</b>", "")[:30]
            lines.append(f"  • {title}...")
    else:
        lines.append("  (조회 실패)")
    lines.append("")

    # ── 4. 추천 액션아이템 ──
    lines.append("*4️⃣ 이번 주 Luca 추천 액션*")
    # 동적 추천 (트렌드 기반)
    if main_trend and main_trend.get("results"):
        r = main_trend["results"][0]
        data = r.get("data", [])
        if data:
            avg = sum(d["ratio"] for d in data) / len(data)
            if avg < 40:
                lines.append("  ⬆️ 검색량 낮음 → 블로그 포스팅 1건 발행 권장")
            elif avg > 70:
                lines.append("  🔥 검색량 높음 → 입찰 단가 +10% 상향 검토")
            else:
                lines.append("  ✅ 검색량 정상 → 현행 전략 유지")
    lines.append("  💡 '남양주 내과' 키워드 광고 그룹 점검")
    lines.append("  💡 경쟁사 '다산 정형외과' 동향 확인")
    lines.append("")
    lines.append("_— Luca 자동화 에이전트 발송 —_")

    return "\n".join(lines)


if __name__ == "__main__":
    report = build_report()
    print(report)
