import re

filepath = r'c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\AIndb_Project\남양주백병원 AI비서 NDB 실무 교육 (초보자용 완전 가이드20260313-Final).html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_step_4 = '''
        <!-- Step 4 -->
        <article class="step-card" style="border-top-color: #0d9488;">
            <div class="step-header">
                <div class="step-number" style="background-color: #0d9488;">4</div>
                <h2 class="step-title">우리 병원 DNA 학습: 공식 홈페이지 기반 기초 지식 습득</h2>
            </div>
            <p>헌법 주입이 끝난 후 비서가 본격적인 업무를 수행하기 전에 우리 남양주백병원의 핵심 진료와 철학을 먼저 이해해야 합니다.</p>

            <div class="sub-step">
                <h4>최초 팩트체크 및 학습 지시</h4>
                <p>비서에게 홈페이지 주소를 주고 스스로 들어가서 학습하라고 명령합니다.</p>
                <div class="prompt-box">"AIndb 부장님! 우리 병원의 공식 홈페이지 주소는 https://www.baekhospital.co.kr/ 야. 지금 즉시 접속해서 우리 병원의 핵심 진료 센터, 자랑할 만한 첨단 장비 목록, 그리고 주요 경영 철학 등을 싹 긁어와서 먼저 스스로 학습하고 결과만 브리핑해 봐."</div>
            </div>
            
            <div class="info-box" style="background-color: #f0fdfa; border-color: #ccfbf1;">
                <h3 style="color: #0f766e; margin-bottom: 10px;">🩺 병원 맞춤형 비서의 완성</h3>
                <p style="color: #115e59; line-height: 1.6;">이렇게 홈페이지를 한 번만 긁게 해두면, 앞으로 환자 응대 멘트나 예약 가이드를 짤 때 <strong>우리 병원에 특화된 전문 지식(예: 척추/관절 센터의 강점, 최소침습 수술 등)</strong>을 알아서 섞어서 답변하게 됩니다. 아주 훌륭한 전략입니다!</p>
            </div>
        </article>
'''

parts = re.split(r'(<!-- Step 4 -->)', content, maxsplit=1)

if len(parts) == 3:
    before = parts[0]
    after = parts[1] + parts[2]
    
    def increment_comment(match):
        num = int(match.group(1))
        return f'<!-- Step {num + 1} -->'
    
    after = re.sub(r'<!-- Step (\d+).*?-->', increment_comment, after)
    
    def increment_div(match):
        prefix = match.group(1)
        num = int(match.group(2))
        suffix = match.group(3)
        return f'{prefix}{num + 1}{suffix}'
    
    after = re.sub(r'(<div class="step-number"[^>]*>)(\d+)(</div>)', increment_div, after)
    
    final_content = before + new_step_4 + after
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("SUCCESS: Inserted Step 4 and shifted all subsequent steps.")
else:
    print("ERROR: Could not find '<!-- Step 4 -->' split point.")
