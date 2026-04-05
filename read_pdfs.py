import PyPDF2
import glob
import os

pdf_dir = r"C:\Users\USER\OneDrive\바탕 화면\통합돌봄"
pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

output_file = r"c:\Users\USER\OneDrive\바탕 화면\luca연구에이전트\pdf_summary.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                out.write(f"--- File: {os.path.basename(pdf_file)} ({num_pages} pages) ---\n")
                
                text = ""
                # Extract text from all pages
                for i in range(num_pages):
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # Write first 5000 chars as a summary
                out.write(text[:5000])
                out.write("\n" + "="*50 + "\n\n")
        except Exception as e:
            out.write(f"Error reading {pdf_file}: {e}\n")
print(f"Extraction complete. Saved to {output_file}")
