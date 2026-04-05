import fitz
doc = fitz.open(r'C:\Users\USER\OneDrive\바탕 화면\남양주백병원ERP\신환환자창출TF\네이버 온라인 광고 운영 현황 보고.pdf')
with open(r'c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\pdf_content.txt', 'w', encoding='utf-8') as f:
    for page in doc:
        f.write(page.get_text())
