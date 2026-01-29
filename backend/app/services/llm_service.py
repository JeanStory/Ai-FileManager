"""
大模型服务封装 - 基于langchain
"""
from typing import List, Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    """
    LLM服务类
    """
    def __init__(self, model_name: str = None, temperature: float = 0.7):
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL
        self.temperature = temperature
        self.chat_histories = {} # 存储用户对话历史
        self.vector_store = {} # 存储向量数据库
        pass
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        user_id: str = None,
        stream: bool=False
    ):
        """
        调用大模型进行对话
        """
        return NotImplementedError("子类必须实现此方法")

    async def process_with_context(
        self,
        query: str,
        context_docs: List[Document],
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        基于上下文处理查询
        """
        return NotImplementedError("子类必须实现此方法")
    
    def _create_memory(self, user_id:str) -> ConversationBufferMemory:
        """
        创建用户对话历史内存
        """
        return ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

def create_service():
    """
    创建LLM服务实例
    """
    return LLMService()


_llm_service_instance = None
def get_llm_service() -> LLMService:
    """
    获取LLM服务实例(单例模式)
    """

    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = create_service()
    return _llm_service_instance
