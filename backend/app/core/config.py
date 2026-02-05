"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    应用设置
    """

    # 应用配置
    APP_NAME: str = "Ai-FileManager"
    Debug: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"

    # LLM配置
    LLM_MODEL: str = "deepseek/deepseek-v3.2"
    LLM_BASE_URL: Optional[str] = "https://api.ppinfra.com/anthropic"
    LLM_API_KEY: Optional[str] = "sk_00VtwP-DW6rME60bF3YzqZTCIoNqK2Dh3g9Oo8W4G98"

    # OCR配置
    OCR_MODEL: str = "qwen-vl-ocr-latest"
    OCR_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    OCR_API_KEY: Optional[str] = "xxxxx"

    # 向量存储配置
    VECTOR_STORE_PATH: str = "./data/vector_store"

    # 文件上传配置
    TEMP_DIR: str = "./temp"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024 # 100MB

    # CORS配置
    ALLOWED_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

# 全局配置实例
settings = Settings()