import re

filepath = r'c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\AIndb_Project\남양주백병원 AI비서 NDB 실무 교육 (초보자용 완전 가이드20260313-Final).html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

new_step_3 = '''
        <!-- Step 3 -->
        <article class="step-card" style="border-top-color: #8b5cf6;">
            <div class="step-header">
                <div class="step-number" style="background-color: #8b5cf6;">3</div>
                <h2 class="step-title">영구 지침 각인: Global Instructions 주입</h2>
            </div>
            <p>이제 비서에게 <strong>'철학과 행동 원칙(헌법)'</strong>을 주입할 차례입니다. 원장님의 경영 철학과 비서의 소통 방식을 결정짓는 병원 특화 세팅입니다.</p>

            <div class="sub-step">
                <h4>AIndb 헌법 파일 생성 지시</h4>
                <p>앞서 제공받은 <code>aindb_global_instructions.md</code> (AIndb 헌법 및 마스터 운영 지침) 파일의 내용을 비서에게 학습시킵니다. 채팅창에 첨부파일을 추가하고 아래와 같이 입력하세요.</p>
                <div class="prompt-box">"AIndb 부장님! 내가 첨부한 문서의 내용(Top-Down 동기화 규칙, 페르소나, RAG 등)을 너의 영구적인 시스템 프롬프트(Global Instruction)로 각인해 줘. 앞으로 작동할 때 이 헌법을 최우선으로 지켜!"</div>
            </div>
            
            <div class="info-box" style="background-color: #fdf4ff; border-color: #f5d0fe;">
                <h3 style="color: #a21caf; margin-bottom: 10px;">✨ 헌법이 주입되면 무엇이 달라지나요?</h3>
                <ul style="color: #4a044e; line-height: 1.6; padding-left: 20px;">
                    <li>항상 <strong>"원장님, 이 AIndb가 대기 중입니다! 🫡"</strong>와 같이 밝고 공감하는 프로 비서의 태도를 유지합니다.</li>
                    <li>에이전트가 지시 수령 및 완료 보고 시 예쁜 이미지를 활용하여 기분 좋게 인사합니다.</li>
                    <li>모르는 것을 임의로 지어내지 않고(환각 방지), 반드시 정해진 보안망(NotebookLM) 안에서 팩트체크합니다.</li>
                </ul>
            </div>
        </article>
'''

parts = re.split(r'(<!-- Step 3 -->)', content, maxsplit=1)

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
    
    final_content = before + new_step_3 + after
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("SUCCESS: Inserted Step 3 and shifted all subsequent steps.")
else:
    print("ERROR: Could not find '<!-- Step 3 -->' split point.")
