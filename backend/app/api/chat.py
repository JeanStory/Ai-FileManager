"""
AI-FileManager 对话API接口
"""
import json
from fastapi import APIRouter, Depends,WebSocket, WebSocketDisconnect, status, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/completion", response_model=dict)
async def chat_completion(request: Request, current_user: User = Depends(get_current_user)):
    """
    对话完成接口,调用大模型进行对话
    """
    pass

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