

from langchain_core.prompts import ChatPromptTemplate

def create_intent_prompt(message: str) -> str:
    prompt = ChatPromptTemplate.from_messages([
        {"role": "system", "content": """
你是一个意图分析专家，能够根据用户的输入分析出用户的需求。
返回的结果必须严格按照json格式输出，json字符串的key必须是intent，value必须是用户的需求。
'''
{{
    "intent": "用户的需求"
}}
'''
    """},
    {"role": "user", "content": """
请分析以下用户输入的意图：<{message}>
    """},
    ])
   
    return prompt.invoke({"message": message})

def create_planning_prompt(message: str, intent: str) -> str:
    prompt = ChatPromptTemplate.from_messages([{"role": "system", "content": f"""
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
            """}])
   
    return prompt.invoke({"message": message, "intent": intent})