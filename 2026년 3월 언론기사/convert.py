import os
import glob
import markdown
import shutil
import base64

base_dir = r"c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\2026년 3월 언론기사"
brain_dir = r"c:\Users\USER\.gemini\antigravity\brain\367b1a05-1f8f-498c-ab6a-27ba3ff20aa1"
md_dir = os.path.join(base_dir, "1_Markdown")
html_dir = os.path.join(base_dir, "2_HTML")
docs_dir = os.path.join(base_dir, "3_Docs")
pdf_dir = os.path.join(base_dir, "4_PDF")

image_map = {
    "1_봄철_허리통증과_다리저림": "news_spine_pain_1772594264017.png",
    "뇌신경센터_경도인지장애": "news_dementia_test_1772594281042.png",
    "관절센터_스포츠손상_초기치료": "news_sports_injury_1772594299306.png",
    "가정의학과_만성질환": "news_chronic_immunity_1772594324067.png",
    "응급진료실_봄철사고": "news_er_spring_1772594340645.png",
    "뇌신경_소화기_대상포진": "news_shingles_neuro_1772594357819.png"
}

try:
    import win32com.client
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0 
    word_available = True
except Exception as e:
    print(f"Failed to initialize Word automation: {e}")
    word_available = False

css_style = """
<style>
    body { font-family: 'Malgun Gothic', 'Nanum Gothic', sans-serif; line-height: 1.7; color: #2c3e50; max-width: 800px; margin: 0 auto; padding: 40px 20px; background-color: #fcfcfc;}
    .news-container { background: #fff; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .hospital-logo { font-size: 24px; font-weight: 900; color: #1e3799; border-bottom: 3px solid #1e3799; padding-bottom: 10px; margin-bottom: 30px; letter-spacing: -1px; }
    h1 { color: #2c3e50; font-size: 28px; font-weight: 800; line-height: 1.4; margin-bottom: 25px; word-break: keep-all; }
    .hero-image { width: 100%; max-height: 450px; object-fit: cover; border-radius: 6px; margin: 25px 0; }
    h2, h3 { color: #1e3799; font-weight: 700; margin-top: 35px; }
    p { font-size: 16px; margin-bottom: 20px; text-align: justify; word-break: keep-all;}
    strong { color: #000; background-color: #f1f8ff; padding: 2px 5px; }
    blockquote { border-left: 4px solid #1e3799; margin: 0; padding-left: 15px; background: #f8f9fa; padding: 15px; font-style: italic; }
    hr { border: 0; border-top: 1px solid #eee; margin: 40px 0; }
    .hospital-info { background: #f8f9fa; padding: 20px; border-radius: 6px; font-size: 15px; border-left: 4px solid #27ae60; }
    .footer { text-align: center; margin-top: 40px; font-size: 13px; color: #7f8c8d; }
</style>
"""

md_files = glob.glob(os.path.join(md_dir, "*.md"))

for md_path in md_files:
    filename = os.path.basename(md_path)
    base_name = os.path.splitext(filename)[0]
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    html_content = markdown.markdown(md_text, extensions=['tables'])
    
    img_tag = ""
    if base_name in image_map:
        img_file = os.path.join(brain_dir, image_map[base_name])
        if os.path.exists(img_file):
            with open(img_file, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            img_tag = f'<img class="hero-image" src="data:image/png;base64,{encoded_string}" alt="Medical Scene" />'
        
    full_html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset='utf-8'>
        {css_style}
    </head>
    <body>
        <div class="news-container">
            <div class="hospital-logo">Medical News | 남양주 백병원</div>
            {img_tag}
            {html_content}
            <div class="footer">© 2026 Namyangju Baek Hospital. All rights reserved.</div>
        </div>
    </body>
    </html>
    """
    
    html_path = os.path.join(html_dir, f"{base_name}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Created Premium HTML: {html_path}")
    
    if word_available:
        try:
            doc = word.Documents.Open(html_path, ConfirmConversions=False, ReadOnly=True)
            docx_path = os.path.join(docs_dir, f"{base_name}.docx")
            doc.SaveAs(docx_path, 16)
            print(f"Created DOCX: {docx_path}")
            
            pdf_path = os.path.join(pdf_dir, f"{base_name}.pdf")
            doc.SaveAs(pdf_path, 17)
            print(f"Created PDF: {pdf_path}")
            
            doc.Close(0)
        except Exception as e:
            print(f"Failed converting via Word for {base_name}: {e}")
            
if word_available:
    word.Quit()
print("Premium conversion process completed.")
