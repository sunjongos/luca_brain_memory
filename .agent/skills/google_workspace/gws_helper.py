import subprocess
import json
import os
import sys
import logging

logger = logging.getLogger("LucaGWS")

class GWSHelper:
    """Google Workspace CLI (gws)를 위한 자율 래퍼 클래스"""
    
    @staticmethod
    def run_command(args, format_json=True):
        """gws 명령어를 실행하고 결과를 반환합니다."""
        cmd = ["gws"] + args
        if format_json and "--format" not in args:
            cmd += ["--format", "json"]
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=60,
                shell=True
            )
            
            if result.returncode != 0:
                # 🛠️ Self-Correction: 인증 에러 감지 시
                if "auth failed" in result.stderr.lower() or "401" in result.stdout:
                    return {"error": "AUTH_REQUIRED", "message": "Google Workspace 인증이 만료되었거나 설정되지 않았습니다. '/gws_auth' 명령어를 직접 실행해주세요."}
                return {"error": "COMMAND_FAIL", "message": result.stderr or result.stdout}
            
            if format_json:
                try:
                    return json.loads(result.stdout)
                except:
                    return {"content": result.stdout.strip()}
            return result.stdout.strip()
            
        except Exception as e:
            return {"error": "SYSTEM_ERROR", "message": str(e)}

    @classmethod
    def get_version(cls):
        """현재 gws CLI 버전을 확인합니다."""
        res = cls.run_command(["--version"], format_json=False)
        return res.split("\n")[0] if isinstance(res, str) else "Unknown"

    @classmethod
    def check_and_update(cls):
        """gws CLI를 최신 버전으로 업데이트합니다 (Self-evolution)."""
        logger.info("GWS CLI 업데이트 체크 중...")
        try:
            res = subprocess.run(
                ["npm", "update", "-g", "@googleworkspace/cli"],
                capture_output=True, text=True, timeout=120
            )
            return {"success": res.returncode == 0, "output": res.stdout, "error": res.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @classmethod
    def get_available_commands(cls):
        """gws --help를 분석하여 현재 사용 가능한 모든 서비스를 동적으로 탐지합니다."""
        help_text = cls.run_command(["--help"], format_json=False)
        if not isinstance(help_text, str):
            return []
        
        commands = []
        capture = False
        for line in help_text.split("\n"):
            if "SERVICES:" in line:
                capture = True
                continue
            if capture:
                stripped = line.strip()
                if not stripped: continue
                # 섹션이 끝나면 중단
                if line.startswith("ENVIRONMENT:") or line.startswith("FLAGS:"):
                    break
                # 서비스명 추출 (줄 시작부터 첫 공백 전까지)
                cmd_name = stripped.split()[0]
                if cmd_name.islower(): # 서비스명은 소문자로 시작함
                    commands.append(cmd_name)
        return commands

if __name__ == "__main__":
    helper = GWSHelper()
    print(f"GWS Version: {helper.get_version()}")
    cmds = helper.get_available_commands()
    print(f"Available Services: {cmds}")
    
    if "gmail" in cmds:
        print("--- Testing Gmail Triage ---")
        res = helper.run_command(["gmail", "+triage"])
        print(json.dumps(res, indent=2, ensure_ascii=False))
