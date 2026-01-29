"""
API 模块
"""
from fastapi import APIRouter

# 创建主路由器
api_router = APIRouter()

# 导入并包含子路由
from . import auth, chat

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(chat.router, prefix="/chat", tags=["对话"])
