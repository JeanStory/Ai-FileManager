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
    DEFAULT_LLM_PROVIDER:str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-3.5-turbo"

    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = "https://api.openai.com/v1"

    # 阿里云通义千问配置
    DASHSCOPE_API_KEY: Optional[str] = None

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