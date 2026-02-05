import json
from typing import List, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage

from app.core.prompts import create_intent_prompt, create_planning_prompt
from app.core.config import settings
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
        self.model=ChatAnthropic(
            model=settings.LLM_MODEL, 
            temperature=0.7, 
            base_url=settings.LLM_BASE_URL, 
            api_key=settings.LLM_API_KEY)

    def chat(self, message: str) -> Optional[str]:
        while True:
            intent = self.intent_identify(message)
            if intent  is not  None:
                break
        print(f"intent: {intent}")
        while True:
            plans = self.generate_plan(message, intent)
            if plans  is not None:
                break
        print(f"plans: {plans}")
        return None
    
    def intent_identify(self, message: str) -> Optional[str]:
        intent_messages = create_intent_prompt(message)
        intent_result = self.model.invoke(intent_messages)
        try:
            intent_result = json.loads(intent_result.content)
            if "intent" not in intent_result:
                logger.warning(f"意图分析结果缺少intent字段: {intent_result}")
                return None
        except json.JSONDecodeError:
                logger.error(f"意图分析结果不是有效JSON格式: {intent_result}")
                return None

        return intent_result["intent"]
    
    def generate_plan(self, message: str, intent: str) -> Optional[List[str]]:
        planning_messages = create_planning_prompt(message, intent)
        planning_result = self.model.invoke(planning_messages)
        try:
            plans = json.loads(planning_result.content)
            if not isinstance(plans, list):
                logger.warning(f"计划生成结果不是有效JSON格式: {plans}")
        except json.JSONDecodeError:
            logger.error(f"计划生成结果不是有效JSON格式: {planning_result.content}")
            return None
        
        return plans

    def excute_plan(self, plans: List[str]) -> Optional[str]:
        excutor_messages = [SystemMessage(content="你是一个实施专家，能够调用各种的工具来完成客户的计划")]
        checker_messages = []
        for plan in plans:
            while True:
                excutor_messages.append(HumanMessage(content=plan))
                response = self.model.invoke(excutor_messages)
                excutor_messages.append(AIMessage(content=response.content))

        summary_messages = [SystemMessage(content="你是一个总结专家，能够根据实施结果生成一个总结")]
        summary_messages.extend(excutor_messages)
        summary_result = self.model.invoke(summary_messages)
        try:
            summary = json.loads(summary_result.content)
            if "summary" not in summary:
                logger.warning(f"总结生成结果缺少summary字段: {summary}")
        except json.JSONDecodeError:
                logger.error(f"总结生成结果不是有效JSON格式: {summary_result.content}")
                return None
        
        return summary["summary"]
