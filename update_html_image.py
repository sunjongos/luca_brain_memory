import os
import shutil

src_img = r"C:\Users\USER\.gemini\antigravity\brain\38cff608-8cd3-4ac2-96c6-15743be9d9e4\sleep_apnea_stroke_connection_1774340287235.png"
dest_img = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_image.png"
html_path = r"C:\Users\USER\OneDrive\바탕 화면\언론기사\2026년 3월 언론기사\뇌신경센터\sleep_apnea_stroke_article.html"

# Copy image
shutil.copy2(src_img, dest_img)

# Update HTML
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

img_tag = '\n<img src="sleep_apnea_stroke_image.png" alt="수면무호흡증과 뇌출혈 연관성" style="width:100%; max-width:700px; display:block; margin:40px auto; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.15);">\n'

# Insert the image tag right after <div class="article-body">
search_str = '<div class="article-body">'
if search_str in content and 'sleep_apnea_stroke_image.png' not in content:
    new_content = content.replace(search_str, search_str + img_tag, 1)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("HTML updated securely with the image.")
else:
    print("HTML already contains the image or parse failed.")
