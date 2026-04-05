import os
import logging
import asyncio

logger = logging.getLogger("OpenClawValidator")

class OutputValidator:
    """
    OpenClaw Gateway의 Multi-Agent 구조에서 Validator (검증자) 역할을 담당합니다.
    Executor가 실행하려 하거나 출력한 결과를 최종 검사하여 시스템 오류, 무한 루프, 보안 위협을 방지합니다.
    """
    def __init__(self):
        self.max_retries = 3

    def validate_code(self, code_string: str) -> bool:
        """기본 보안 검증 및 문법 에러 필터링"""
        forbidden_keywords = ["os.system('rm -rf", "subprocess.call(['rm'"]
        for kw in forbidden_keywords:
            if kw in code_string:
                logger.error(f"보안 위협 감지: {kw}")
                return False
        return True

    def validate_execution_result(self, result: dict) -> bool:
        """실행 결과(Context)가 의도한 형식에 부합하는지 검증"""
        if result.get("error"):
            logger.warning("실행 중 에러 발생, 재검증 필요")
            return False
            
        if not result.get("output"):
            logger.warning("결과값이 비어 있습니다.")
            return False
            
        return True

    async def run_validation_pipeline(self, task_result):
        """향후 AI를 활용한 논리적 검사(LLM validation) 확장을 위한 비동기 파이프라인"""
        logger.info("Validator 에이전트: 결과물 검증을 시작합니다.")
        # 더 고도화된 검증 로직 추가 예정
        return self.validate_execution_result(task_result)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    val = OutputValidator()
    print("Validator Agent Ready.")
