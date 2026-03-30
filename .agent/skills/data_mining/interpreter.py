import os
import sys
import subprocess
import tempfile
import json
import pandas as pd
from pathlib import Path

# Setup paths and environment
BASE_DIR = Path(__file__).parent.parent.parent.parent
_env_file = BASE_DIR / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        _line = _line.replace('\x00', '').strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.replace('\x00', '').strip().strip('"').strip("'"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("❌ OPENAI_API_KEY is missing.")
    sys.exit(1)

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_data(prompt, file_path=None):
    data_context = ""
    # Provide data context if a file is provided
    if file_path and os.path.exists(file_path):
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=5)
                data_context = f"\nData Context:\nFile Path: {file_path}\nColumns: {list(df.columns)}\nSample Rows:\n{df.head().to_string()}\n"
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path, nrows=5)
                data_context = f"\nData Context:\nFile Path: {file_path}\nColumns: {list(df.columns)}\nSample Rows:\n{df.head().to_string()}\n"
        except Exception as e:
            data_context = f"\nWarning: Failed to preview data file. {e}\n"

    system_prompt = """You are an expert Python data scientist for the 'Luca Super Agent'.
Write a Python script that fulfills the user's data analysis request.
RULES:
1. ONLY output the raw Python code. Do not include markdown formatting like ```python.
2. The code must be safe and syntactically correct.
3. If the user asks for a plot or chart, SAVE IT to a file named 'luca_plot.png' in the current working directory, and DO NOT call plt.show().
4. Print your textual analysis results cleanly to STDOUT so the user can read them. Focus on business insights.
"""

    user_request = prompt + data_context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_request}
        ],
        temperature=0.2
    )

    generated_code = response.choices[0].message.content.strip()
    if generated_code.startswith("```python"):
        generated_code = generated_code.replace("```python", "").replace("```", "").strip()
    elif generated_code.startswith("```"):
        generated_code = generated_code.replace("```", "").strip()

    # Execute the generated code
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as script_file:
        script_file.write(generated_code)
        script_path = script_file.name

    cwd = os.getcwd()
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd
        )
        output = result.stdout + result.stderr

        # Check for generated image
        plot_path = os.path.join(cwd, "luca_plot.png")
        if os.path.exists(plot_path):
            output += f"\n[IMAGE_GENERATED] {plot_path}"

        print(output.strip())
    except subprocess.TimeoutExpired:
        print("❌ 실행 시간 초과 (60초). 복잡한 쿼리이거나 데이터가 너무 많습니다.")
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
    finally:
        os.unlink(script_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <prompt> [file_path]")
        sys.exit(1)
        
    user_prompt = sys.argv[1]
    data_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyze_data(user_prompt, data_file)
