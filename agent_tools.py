import os
import sys
import subprocess
import logging
import io
import contextlib
import signal
import threading
from pathlib import Path

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# 1. 터미널 명령어 실행
# ─────────────────────────────────────────
def run_terminal_command(command: str) -> str:
    """터미널 명령어(CMD/PowerShell)를 실행하고 반환값을 가져옵니다."""
    try:
        logger.info(f"실행: {command}")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='cp949',
            errors='ignore',
            timeout=60,
            env=env
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return output or "[명령어 실행 완료 (출력 없음)]"
    except subprocess.TimeoutExpired:
        return "⏱️ 명령어 실행 시간 초과 (60초)"
    except Exception as e:
        return f"터미널 명령어 실행 실패: {e}"


# ─────────────────────────────────────────
# 2. 로컬 파일 읽기
# ─────────────────────────────────────────
def read_local_file(path: str) -> str:
    """로컬 파일을 읽어서 문자열로 반환합니다."""
    try:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            return f"❌ 파일을 찾을 수 없습니다: {abs_path}"
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if len(content) > 4000:
            content = content[:4000] + "\n\n... (내용이 너무 길어 생략됨)"
        return content
    except Exception as e:
        return f"파일 읽기 실패: {e}"


# ─────────────────────────────────────────
# 3. 로컬 파일 쓰기
# ─────────────────────────────────────────
def write_local_file(path: str, content: str) -> str:
    """지정한 경로에 파일(내용 포함)을 생성하거나 덮어씁니다."""
    try:
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 파일 저장 완료: {abs_path}"
    except Exception as e:
        return f"파일 저장 실패: {e}"


# ─────────────────────────────────────────
# 4. 디렉토리 탐색 (NEW)
# ─────────────────────────────────────────
def list_directory(path: str = ".") -> str:
    """지정 경로의 파일/폴더 목록을 반환합니다."""
    try:
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            return f"❌ 디렉토리가 아닙니다: {abs_path}"
        items = sorted(Path(abs_path).iterdir(), key=lambda x: (not x.is_dir(), x.name))
        lines = [f"📁 {abs_path}"]
        for item in items[:50]:
            if item.is_dir():
                lines.append(f"  📂 {item.name}/")
            else:
                size_kb = item.stat().st_size / 1024
                lines.append(f"  📄 {item.name} ({size_kb:.1f}KB)")
        if len(items) > 50:
            lines.append(f"  ... 외 {len(items) - 50}개")
        return "\n".join(lines)
    except Exception as e:
        return f"디렉토리 탐색 실패: {e}"


# ─────────────────────────────────────────
# 5. 웹 URL 스크래핑 (NEW)
# ─────────────────────────────────────────
def browse_url(url: str) -> str:
    """URL의 웹 페이지 내용을 읽어서 텍스트로 반환합니다."""
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding

        soup = BeautifulSoup(resp.text, "html.parser")
        # 불필요한 태그 제거
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "ads"]):
            tag.decompose()

        # 본문 텍스트 추출
        text = soup.get_text(separator="\n", strip=True)
        # 빈 줄 압축
        lines = [l for l in text.splitlines() if l.strip()]
        result = "\n".join(lines)

        if len(result) > 5000:
            result = result[:5000] + "\n\n...(이하 생략)"
        return f"🌐 [{url}] 내용:\n\n{result}"
    except Exception as e:
        return f"❌ URL 읽기 실패: {e}"


# ─────────────────────────────────────────
# 6. 웹 검색 — DuckDuckGo (NEW)
# ─────────────────────────────────────────
def web_search(query: str, max_results: int = 5) -> str:
    """DuckDuckGo로 웹 검색 후 결과 반환합니다 (API 키 불필요)."""
    try:
        # User local packages path
        user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python312\site-packages")
        if user_site not in sys.path:
            sys.path.insert(0, user_site)

        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(
                    f"🔗 **{r.get('title', '')}**\n"
                    f"   {r.get('href', '')}\n"
                    f"   {r.get('body', '')[:200]}"
                )
        if not results:
            return "🔍 검색 결과가 없습니다."
        return f"🔍 **'{query}' 검색 결과 (DuckDuckGo)**\n\n" + "\n\n".join(results)
    except Exception as e:
        return f"❌ 웹 검색 실패: {e}"


# ─────────────────────────────────────────
# 7. Python REPL 실행 (NEW)
# ─────────────────────────────────────────
def execute_python(code: str) -> str:
    """Python 코드를 안전하게 실행하고 stdout 결과를 반환합니다."""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    result_container = {"output": "", "error": ""}

    def _run():
        try:
            local_ns = {}
            with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
                exec(compile(code, "<luca_repl>", "exec"), {"__builtins__": __builtins__}, local_ns)
            result_container["output"] = stdout_buf.getvalue()
        except Exception as ex:
            result_container["error"] = str(ex)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=10)

    if t.is_alive():
        return "⏱️ 코드 실행 시간 초과 (10초)"

    if result_container["error"]:
        return f"❌ 실행 에러:\n```\n{result_container['error']}\n```"

    output = result_container["output"].strip()
    if not output:
        # 마지막 식의 평가값을 가져오려고 시도
        try:
            lines = code.strip().split("\n")
            last = lines[-1]
            val_buf = io.StringIO()
            local_ns2 = {}
            with contextlib.redirect_stdout(val_buf):
                exec(compile("\n".join(lines[:-1]), "<luca_setup>", "exec"), {}, local_ns2)
                result = eval(compile(last, "<luca_eval>", "eval"), {}, local_ns2)
                output = str(result)
        except Exception:
            output = "[실행 완료, 출력 없음]"

    return f"🐍 **Python 실행 결과:**\n```\n{output[:3000]}\n```"
