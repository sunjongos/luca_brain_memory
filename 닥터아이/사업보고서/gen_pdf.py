from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

PDF_PATH = r'C:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\닥터아이\사업보고서\사업보고서_닥터아이_MultiAgent.pdf'

# ── 한글 폰트 등록
FONT_PATHS = [
    r'C:\Windows\Fonts\malgun.ttf',
    r'C:\Windows\Fonts\NanumGothic.ttf',
    r'C:\Windows\Fonts\gulim.ttc',
]
FONT_NAME = 'Korean'
for fp in FONT_PATHS:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, fp))
            print(f'폰트 등록: {fp}')
            break
        except:
            continue

FONT_BOLD = FONT_NAME  # fallback

# ── 색상
NAVY    = colors.HexColor('#0B1F3A')
BLUE    = colors.HexColor('#1A4DB3')
TEAL    = colors.HexColor('#00C9B1')
RED     = colors.HexColor('#E84545')
GOLD    = colors.HexColor('#F5A623')
PURPLE  = colors.HexColor('#7C3AED')
GREEN   = colors.HexColor('#10B981')
LGRAY   = colors.HexColor('#F0F4F9')
WHITE   = colors.white

# ── 스타일
def make_styles():
    s = {}
    fn = FONT_NAME
    s['cover_title'] = ParagraphStyle('ct', fontName=fn, leading=26, fontSize=22, textColor=WHITE, spaceAfter=10, alignment=1)
    s['cover_sub']   = ParagraphStyle('cs', fontName=fn, leading=18, fontSize=12, textColor=colors.HexColor('#A0B0CC'), spaceAfter=6, alignment=1)
    s['cover_meta']  = ParagraphStyle('cm', fontName=fn, leading=15, fontSize=10, textColor=colors.HexColor('#7080A0'), spaceAfter=4, alignment=1)
    s['h1']  = ParagraphStyle('h1', fontName=fn, leading=22, fontSize=16, textColor=NAVY, spaceBefore=16, spaceAfter=6)
    s['h2']  = ParagraphStyle('h2', fontName=fn, leading=18, fontSize=13, textColor=BLUE, spaceBefore=12, spaceAfter=4)
    s['h3']  = ParagraphStyle('h3', fontName=fn, leading=15, fontSize=11, textColor=TEAL, spaceBefore=8, spaceAfter=3)
    s['body']= ParagraphStyle('body', fontName=fn, leading=17, fontSize=10, textColor=colors.HexColor('#374151'), spaceAfter=6)
    s['th']  = ParagraphStyle('th', fontName=fn, leading=13, fontSize=9, textColor=WHITE, alignment=1)
    s['td']  = ParagraphStyle('td', fontName=fn, leading=13, fontSize=9, textColor=colors.HexColor('#374151'))
    s['note']= ParagraphStyle('note', fontName=fn, leading=17, fontSize=10, textColor=NAVY, backColor=colors.HexColor('#E8F4FD'), spaceAfter=8)
    return s

S = make_styles()

def h1(text): return [Paragraph(text, S['h1']), HRFlowable(color=TEAL, thickness=2, spaceAfter=8)]
def h2(text): return [Paragraph(text, S['h2'])]
def h3(text): return [Paragraph(text, S['h3'])]
def body(text): return Paragraph(text, S['body'])
def note(text): return Paragraph(f'<b>💡</b> {text}', S['note'])
def sp(h=6): return Spacer(1, h*mm)

# ── 표 스타일
def tbl_style(extra=None):
    ts = [
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('TEXTCOLOR', (0,0), (-1,0), WHITE),
        ('FONTNAME', (0,0), (-1,0), FONT_NAME),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LGRAY]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D9E6')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
    ]
    if extra:
        ts.extend(extra)
    return TableStyle(ts)

def make_table(data, col_widths=None):
    rows = []
    for i, row in enumerate(data):
        rows.append([Paragraph(str(c), S['th'] if i==0 else S['td']) for c in row])
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(tbl_style())
    return t

# ── 문서 생성
doc = SimpleDocTemplate(PDF_PATH, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

story = []

# ────────────────── COVER PAGE ──────────────────
from reportlab.platypus import KeepInFrame
# 커버: 배경색 블록 대신 텍스트만
story.append(sp(30))
story.append(Paragraph('[ 대외비 · 사업보고서 ]', S['cover_meta']))
story.append(sp(10))
story.append(Paragraph('닥터아이 Multi-Agent\n당뇨 눈 질환 관리 시스템', S['cover_title']))
story.append(sp(8))
story.append(Paragraph('세계 최초 — AI 안저진단 + 다중 에이전트 오케스트레이션으로\n당뇨성 실명을 막는 의료 자동화 플랫폼 사업 제안', S['cover_sub']))
story.append(sp(20))
story.append(Paragraph('PaiHealthcare-LCK 연구소 | 닥터아이 (Doctor Eye)\n2026년 03월 07일', S['cover_meta']))
story.append(PageBreak())

# ────────────────── 1. 사업 개요 ──────────────────
story += h1('1. 사업 개요')
story.append(body('본 사업은 파이헬스케어-LCK 연구소가 개발한 AI 안저진단 솔루션 닥터아이(Doctor Eye)를 핵심 엔진으로, Multi-Agent AI 시스템을 결합하여 당뇨 환자의 눈 질환을 자동화된 3단계 워크플로우로 관리하는 세계 최초의 의료 AI 오케스트레이션 플랫폼 구축을 목표로 합니다.'))
story.append(sp())
stats = [
    ['구분', '수치', '설명'],
    ['AI 진단 대상', '4대 질환', '당뇨망막증·녹내장·황반변성·망막혈관폐쇄'],
    ['전문 AI 에이전트', '7개 이상', '병렬·직렬 실행으로 워크플로우 자동화'],
    ['조기 발견 예방률', '95%', '당뇨 합병증 실명 예방 의학적 근거'],
    ['AI 판독 시간', '5분 이내', '촬영 후 전자동 리포트 생성 및 EMR 연동'],
]
story.append(make_table(stats, [5*cm, 3*cm, 9.5*cm]))
story.append(sp())
story.append(note('핵심 혁신: 기존 AI 의료 솔루션이 진단에 그쳤다면, 본 시스템은 진단→처방 초안→협진 의뢰→환자 알림→재방문 예약까지 의료 업무 전 과정을 Multi-Agent가 자동 처리하며, 중요한 의사결정만 의사가 Human-in-the-Loop 방식으로 승인합니다.'))
story.append(PageBreak())

# ────────────────── 2. 문제 정의 ──────────────────
story += h1('2. 문제 정의 — 왜 지금인가')
story += h2('2.1 당뇨 합병증 실명의 위험성')
story.append(body('대한민국 당뇨 환자는 약 600만 명. 당뇨성 망막증 발생률은 진단 10년 후 30%에 달하며, 초기 90%가 무증상으로 진행됩니다. 당뇨성 실명은 대한민국 후천성 실명 원인 1위이며, 조기 발견 시 95%가 예방 가능합니다.'))
story += h2('2.2 현재 의료 시스템의 한계')
prob = [
    ['문제', '현황', '결과'],
    ['안저검사 누락', '당뇨 외래 안저검사 시행률 30% 미만', '진단 지연 → 실명'],
    ['단절된 워크플로우', '진단·처방·협진이 각각 분리 운영', '의료 질 편차 발생'],
    ['의사 업무 과부하', '반복적 오더 작성·협진 의뢰 수작업', '진료 집중도 저하'],
    ['환자 추적 실패', '재방문 주기 관리 없음', '고위험군 이탈'],
]
story.append(make_table(prob, [4*cm, 7*cm, 6.5*cm]))
story.append(PageBreak())

# ────────────────── 3. 솔루션 ──────────────────
story += h1('3. 솔루션 — 닥터아이 + Multi-Agent 시스템')
story += h2('3.1 시스템 아키텍처 (4개 레이어)')
layers = [
    ['레이어', '구성', '자동화 수준'],
    ['Layer 1 진단', '닥터아이 AI 안저분석, 위험도 스코어링', '완전 자동'],
    ['Layer 2 처리', 'Prescription·ECAS·Notify·Scheduler Agent 병렬 실행', '완전 자동'],
    ['Layer 3 승인', '처방 최종 승인·협진 서명·고위험 MRI 의뢰', '의사 필수 개입'],
    ['Layer 4 학습', '처방 이력 학습·개인화 모델 진화', '자동 배치'],
]
story.append(make_table(layers, [4*cm, 9.5*cm, 4*cm]))
story.append(sp())
story += h2('3.2 Agent 구성 및 역할')
agents = [
    ['Agent명', '역할', '실행방식', '의사개입'],
    ['Screening Agent', '닥터아이 결과 수신·위험도 분류', '자동', '없음'],
    ['Risk Scoring Agent', 'X-ECAS 경동맥 위험도 계산', '자동', '없음'],
    ['Prescription Draft Agent', 'EMR 오더셋 처방 초안 생성', '자동 초안', '승인 필요'],
    ['Referral Agent', '협진 의뢰서 자동 작성', '자동 초안', '서명 필요'],
    ['Patient Notify Agent', '결과 문자·앱 알림 발송', '자동', '없음'],
    ['Scheduler Agent', '다음 방문 일정 자동 예약', '자동', '없음'],
    ['Alert Agent', 'High-Risk 긴급 의사 알림', '즉시 알림', '필수'],
    ['Learning Agent', '처방 이력 학습·모델 개선', '배치 자동', '없음'],
]
story.append(make_table(agents, [4.5*cm, 6.5*cm, 3*cm, 3.5*cm]))
story.append(PageBreak())

# ────────────────── 4. 3단계 워크플로우 ──────────────────
story += h1('4. 3단계 임상 워크플로우')
story += h2('Stage 1 — 닥터아이 AI 안저검사')
story.append(body('E6670 코드로 안저촬영. 닥터아이 AI가 5분 내 4대 안질환 분석, 위험도 리포트 자동 생성 → EMR 팝업 연동. 정상 시 6~12개월 자동 재방문 예약. 이상 소견 시 자동으로 2단계 이행.'))
story += h2('Stage 2 — 내과 조치 및 약물 처방')
story.append(body('Prescription Draft Agent가 칼슘 도베실레이트 bid + 징코빌로바 추출물 처방 초안 생성. 의사 검토·승인 후 확정. 동시에 X-ECAS 검사 오더 자동 생성.'))
story += h2('Stage 3 — X-ECAS 위험도별 처치')
risk = [
    ['위험도', '약물 처치', '검사', '협진'],
    ['LOW', '기존 요법 유지', '닥터아이 6~12개월 추적', '불필요'],
    ['INTERMEDIATE', '스타틴 + 항혈소판제', '경동맥 재초음파 6~12개월', '순환기내과 컨설트'],
    ['HIGH', '고강도 스타틴 + 항혈소판제', '뇌 MRI+MRA (의사 필수)', '신경과·순환기내과'],
]
story.append(make_table(risk, [3*cm, 5.5*cm, 5.5*cm, 3.5*cm]))
story.append(PageBreak())

# ────────────────── 5. 세계 최초 포지셔닝 ──────────────────
story += h1('5. 세계 최초 포지셔닝 및 경쟁 우위')
comp = [
    ['비교 항목', '기존 의료 AI', '닥터아이 Multi-Agent'],
    ['AI 역할', '단일 진단만', '진단→처방→협진→알림 자동화'],
    ['워크플로우', '의사가 모든 단계 수동 처리', 'Multi-Agent 병렬·직렬 자동화'],
    ['의사 역할', '모든 결정', '핵심 결정만 Human-in-the-Loop'],
    ['학습 능력', '정적 모델', '처방 이력으로 지속 개인화 학습'],
    ['EMR 연동', '별도 입력 필요', '위험도 기반 오더셋 자동 팝업'],
    ['환자 관리', '의사 기억·수동', 'Scheduler Agent 자동 추적'],
]
story.append(make_table(comp, [4.5*cm, 5.5*cm, 7.5*cm]))
story.append(sp())
story.append(note('2026년 현재, 안과 영역(특히 당뇨 눈 질환)에 Multi-Agent 오케스트레이션 + Human-in-the-Loop를 결합한 임상 워크플로우 시스템은 국내외 논문 및 상용 제품에서 발표된 바 없음. 세계 최초 출시 가능 영역.'))
story.append(PageBreak())

# ────────────────── 6. 시장 분석 ──────────────────
story += h1('6. 시장 분석')
mkt = [
    ['구분', '규모', '비고'],
    ['글로벌 안과 AI 시장 (2028)', '$8.7B', '연평균 성장률 38.7%'],
    ['국내 당뇨 환자', '600만명', '고령화로 2030년 700만명 이상'],
    ['국내 내과·가정의학과 의원', '3만+', '1차 타깃 병원'],
    ['글로벌 의료 AI 자동화 시장', '$42B', 'Multi-Agent 워크플로우 급성장'],
]
story.append(make_table(mkt, [6*cm, 3.5*cm, 8*cm]))
story.append(sp())
story += h2('6.1 수익 구조 예상')
rev = [
    ['시기', '도입 병원', '월 매출 추정', '핵심 활동'],
    ['2026 파일럿', '5개', '500만원', '임상 검증, 데이터 수집'],
    ['2027 초기 확장', '50개', '5,000만원', 'EMR 연동 완성, 학술 발표'],
    ['2028 성장', '300개', '3억원', '전국 확산, 보험 수가 등재'],
    ['2029 글로벌', '500개+', '10억원+', '동남아·중동 수출'],
]
story.append(make_table(rev, [3.5*cm, 3*cm, 4*cm, 7*cm]))
story.append(PageBreak())

# ────────────────── 7. 특허 전략 ──────────────────
story += h1('7. 특허 및 지식재산 전략')
patents = [
    ['특허 ①', '당뇨 눈 질환 Multi-Agent 자동화 진료 시스템'],
    ['특허 ②', 'Human-in-the-Loop 기반 의료 AI 처방 승인 방법'],
    ['특허 ③', '안저·경동맥 통합 위험도 AI 스코어링 시스템'],
    ['특허 ④', '의사 처방 이력 학습 개인화 EMR 오더셋 추천 방법'],
]
story.append(make_table(patents, [3*cm, 14.5*cm]))
story.append(PageBreak())

# ────────────────── 8. 실행 계획 ──────────────────
story += h1('8. 실행 계획 (로드맵)')
road = [
    ['시기', '단계', '주요 목표'],
    ['2026 Q2', '파일럿', '닥터아이+2개 Agent 연동, 파일럿 병원 3~5곳, IRB 승인'],
    ['2026 Q4', '시스템 완성', '8개 Agent 전체 구축, EMR 3종 연동, 특허 출원 4건'],
    ['2027', '초기 확산', '50개 병원 도입, 보험 수가 등재 신청, Series A 유치'],
    ['2028', '전국 확장', '300개 병원, 건강보험 연동, 동남아 파트너 계약'],
    ['2029+', '글로벌', '해외 수출 본격화, 당뇨 외 질환 확장, IPO 준비'],
]
story.append(make_table(road, [3*cm, 3.5*cm, 11*cm]))
story.append(PageBreak())

# ────────────────── 9. 결론 ──────────────────
story += h1('9. 결론 — 지금이 기회입니다')
story.append(body('당뇨성 실명은 막을 수 있는 실명입니다. 닥터아이가 보고, Multi-Agent가 움직이고, 의사가 결정합니다. 기술적 혁신 + 의학적 근거 + 세계 최초 포지셔닝이 갖춰진 이 시스템은 대한민국을 의료 AI 자동화의 글로벌 리더로 만들 수 있습니다.'))
story.append(sp(4))
story.append(note('본 사업에 관심 있는 투자자, 병원 파트너, 기술 협력사는 PaiHealthcare-LCK 연구소로 문의 바랍니다.'))

doc.build(story)
print('PDF 저장 완료:', PDF_PATH)
