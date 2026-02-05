import json
from typing import List, Optional
from app.core.llm_service import get_llm_service
from langchain_core.messages import AnyMessage
from app.utils.logger import get_logger

logger = get_logger(__name__)

class Session():
    id: str
    user_id: str
    messages: List[AnyMessage]

    def __init__(self, id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self.messages = []
        self.model=get_llm_service()

    def chat(self, message: str) -> Optional[str]:
        while True:
            intent = self.intent_identify(message)
            if intent  is not  None:
                break
        while True:
            plans = self.generate_plan(message, intent)
            if plans  is not None:
                break
        
        return self.excute_plan(plans)
    
    def intent_identify(self, message: str) -> Optional[str]:
        intent_messages = [
            {"role": "system", "content": f"""
你是一个意图分析专家，能够根据用户的输入分析出用户的需求。
返回的结果必须严格按照json格式输出，json字符串的key必须是intent，value必须是用户的需求。
'''
{{
    "intent": "用户的需求"
}}
'''
            """},
            {"role": "user", "content": f"""
请分析以下用户输入的意图：<{message}>
            """
            }
            ]
        intent_result = self.model.chat_completion(
            messages=intent_messages,
            user_id=str(current_user.id) if current_user else None,
            stream=False
        )
        try:
            intent_result = json.loads(intent_result)
            if "intent" not in intent_result:
                logger.warning(f"意图分析结果缺少intent字段: {intent_result}")
        except json.JSONDecodeError:
                logger.error(f"意图分析结果不是有效JSON格式: {intent_result}")
                return None

        return intent_result["intent"]
    
    def generate_plan(self, message: str, intent: str) -> Optional[List[str]]:
        planning_messages = [{"role": "system", "content": f"""
你是一个计划生成专家，能够结合用户输入和用户的意图生成一个计划。
返回的结果必须严格按照json格式输出，
'''
[
"步骤1:xxxx",
"步骤2:xxxx"
]
'''
                """},
                {"role": "user", "content": f"""
用户输入：<{message}>
用户意图：<{intent}>
            """}]
        planning_result = self.model.chat_completion(
            messages=planning_messages,
            user_id=str(current_user.id) if current_user else None,
            stream=False
        )
        try:
            plans = json.loads(planning_result)
            if not isinstance(plans, list):
                logger.warning(f"计划生成结果不是有效JSON格式: {plans}")
        except json.JSONDecodeError:
            logger.error(f"计划生成结果不是有效JSON格式: {planning_result}")
            return None
        
        return plans

    def excute_plan(self, plan: List[str]):
        excutor_messages = []
        checker_messages = []
        for plan in plans:
            while True:
                excutor_messages.append(HumanMessage(content=plan))
                response = self.model.chat_completion(
                    messages=excutor_messages,
                    user_id=str(current_user.id) if current_user else None,
                    stream=False
                )
                excutor_messages.append(AIMessage(content=response))
