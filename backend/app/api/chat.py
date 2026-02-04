"""
AI-FileManager 对话API接口
"""
import json
from typing import Optional, List
from langchain_core.messages import AnyMessage
from fastapi import APIRouter, Depends,WebSocket, UploadFile, WebSocketDisconnect, status, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.services.llm_service import get_llm_service
from app.utils.logger import get_logger
from app.utils.files import save_file_to_temp
from app.utils.utils import validate_file_type

logger = get_logger(__name__)

router = APIRouter()

class Request(BaseModel):
    message: str
    files: Optional[List[FileItem]] = []
    session_id: Optional[str] = None
    user_id: Optional[str] = None

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
            plans = self.do_plan(message, intent)
            if plans  is not None:
                break
        
        self.excute_plan(plans)
    
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
    
    def do_plan(self, message: str, intent: str) -> Optional[List[str]]:
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

class User():
    id: str
    sessions: List[Session] = []

users: List[User] = []


@router.post("/completion", response_model=dict)
async def chat_completion(request: Request, file: UploadFile = Depends(validate_file_type), current_user: User = Depends(get_current_user)):
    """
    对话完成接口,调用大模型进行对话
    """
    # 检查用户是否存在
    if request.user_id not in users:
        users[request.user_id] = User(id=request.user_id)
    
    # 检查会话是否存在
    if request.session_id not in users[request.user_id].sessions:
        users[request.user_id].sessions.append(Session(id=request.session_id, user_id=request.user_id))
    


    
        
    file_paths = []
    for file in request.files:
        # 将文件存为临时文件
        file_path = await save_file_to_temp(file)
        file_paths.append(file_path)
    
    # 准备消息
    messages = [{"role": "user", "content": request.message}]
    
    # 调用大模型
    response = await llm_service.chat_completion(
        messages=messages,
        file_paths=file_paths,
        user_id=str(current_user.id) if current_user else None,
        stream=False
    )
    
    return response
    

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    流式聊天接口（Server-Sent Events）
    """
    llm_service = get_llm_service()
    
    async def event_generator():
        """SSE事件生成器"""
        try:
            # 准备消息
            messages = [{"role": "user", "content": request.message}]
            
            # 模拟流式响应（实际需要模型支持）
            # 这里简化处理，实际应该调用支持流式的模型
            response = await llm_service.chat_completion(
                messages=messages,
                user_id=str(current_user.id) if current_user else None,
                stream=False  # 注意：需要模型支持stream=True
            )
            
            # 模拟流式输出
            content = response["content"]
            words = content.split()
            
            for i, word in enumerate(words):
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "content": word + " ",
                        "is_final": i == len(words) - 1
                    })
                }
                # 模拟延迟
                import asyncio
                await asyncio.sleep(0.05)
                
        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }
    
    return EventSourceResponse(event_generator())

@router.websocket("/ws/{user_id}")
async def chat_completion_websocket(websocket: WebSocket, user_id: str):
    """
    对话完成接口,调用大模型进行对话(WebSocket)
    """
    pass

@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    获取聊天历史记录
    """
    pass

@router.delete("/history/{message_id}")
async def delete_chat_history(
    message_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    删除单条聊天历史记录
    """
    pass

@router.delete("/history")
async def delete_all_chat_history(
    current_user: User = Depends(get_current_user)
):
    """
    删除所有聊天历史记录
    """
    pass