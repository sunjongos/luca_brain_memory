import os
import sys
import stat
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
dot_git_dir = root_dir / ".git"

if not dot_git_dir.exists() or not dot_git_dir.is_dir():
    print("❌ ERROR: .git 폴더를 찾을 수 없습니다.")
    sys.exit(1)

hooks_dir = dot_git_dir / "hooks"
hooks_dir.mkdir(exist_ok=True)

pre_commit_py_path = hooks_dir / "pre-commit.py"
pre_commit_sh_path = hooks_dir / "pre-commit"

HOOK_SCRIPT_PY = r"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import subprocess

SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z-_]{35}", "Google/Gemini API Key"),
    (r"sk-(proj-|ant-|)[0-9A-Za-z-_]{30,}", "OpenAI/Claude API Key"),
    (r"xox[baprs]-[0-9]{12,}-[0-9]{12,}-[a-zA-Z0-9]{24}", "Slack Token"),
    (r"github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}", "GitHub PAT")
]

FORBIDDEN_FILES = [".env", "credentials.json", "token.json", "secret"]

def check_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            for pattern, name in SECRET_PATTERNS:
                if re.search(pattern, content):
                    return name
    except Exception:
        pass
    return None

def main():
    try:
        result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'], 
                              capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        sys.exit(0)
        
    staged_files = result.stdout.strip().split('\n')
    if not staged_files or staged_files == ['']:
        sys.exit(0)

    leaks = False
    for filepath in staged_files:
        fn = filepath.lower()
        for forbidden in FORBIDDEN_FILES:
            if forbidden in fn and not filepath.endswith(".example") and not filepath.endswith(".md") and not filepath.endswith(".py"):
                # python scripts and markdown docs can mention 'secret' in their filename conditionally
                if forbidden in [".env", "credentials.json", "token.json"]:
                    print(f"\n🚨 [아이언돔 경보] 보안 위배 파일 감지: {filepath}")
                    leaks = True
                
        leak_type = check_file(filepath)
        if leak_type:
            print(f"\n🚨 [아이언돔 경보] 하드코딩된 API 키 감지: {filepath} ({leak_type})")
            leaks = True

    if leaks:
        print("\n💥 커밋(Commit)이 강제 폭파되었습니다. 보안 이슈를 해결한 뒤 다시 시도하십시오.\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""

HOOK_SCRIPT_SH = """#!/bin/sh
python .git/hooks/pre-commit.py
"""

with open(pre_commit_py_path, "w", encoding="utf-8") as f:
    f.write(HOOK_SCRIPT_PY)

with open(pre_commit_sh_path, "w", encoding="utf-8", newline='\n') as f:
    f.write(HOOK_SCRIPT_SH)

# 실행 권한 부여
os.chmod(pre_commit_py_path, os.stat(pre_commit_py_path).st_mode | stat.S_IEXEC)
os.chmod(pre_commit_sh_path, os.stat(pre_commit_sh_path).st_mode | stat.S_IEXEC)

print("🛡️ [아이언돔 설치 완료 (Win/Mac 호환)] 깃허브 업로드 전면 보안 감시가 가동되었습니다!")
