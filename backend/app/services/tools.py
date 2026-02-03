import os
import sys
import base64
import io

from openai import OpenAI
from langchain_core.tools import tool
from typing import List
from pdf2image import convert_from_path

from pydantic import BaseModel, Field

from core.config import settings


class PdfSplitSchema(BaseModel):
    """
    PDF文件拆分参数模型
    """
    file_path: str = Field(description="单个PDF文件的路径")
    
    

#@tool(description="PDF文件拆分工具,将单个PDF文件拆分成多个PDF文件", args_schema=PdfSplitSchema)
def pdf_split(file_path: str) -> dict:
    """
    文件操作工具,将单个PDF文件拆分成多个PDF文件
    输入:
        file_path: 单个PDF文件的路径
    输出:
        dict: 多个PDF文件的路径列表
    功能:
        将单个PDF文件拆分成多个PDF文件
    示例:
        pdf_split(file_path="example.pdf")
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件路径 {file_path} 不存在")

    # PDF 拆分成多个Images
    image_base64s = []
    images = convert_from_path(file_path)
    with io.BytesIO() as buffer:
        for i, image in enumerate(images):
            # 临时保存每个Image，命名不能冲突
            image.save(buffer, format="JPEG")
            image_base64s.append(base64.b64encode(buffer.getvalue()).decode('utf-8'))

    ocr_client = OpenAI(
        api_key=settings.OCR_API_KEY,
        base_url=settings.OCR_API_URL,
    )
    result = []
    for i, base64_image in enumerate(image_base64s):
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                        }
                    },
                    {
                        "type": "text",
                        "text": "请识别图片中的文本"
                    }
                ]
            }
        ]
        # 调用OCR模型识别图片中的文本
        response = ocr_client.chat.completions.create(
            model=settings.OCR_MODEL,
            messages=messages
        )
        result.append({"page": i, "text": response.choices[0].message.content})
        print(f"第{i}页识别到的文本内容: {response.choices[0].message.content}")
    

    return result

@tool
def pdf_save(file_paths: List[str]) -> bool:
    """
    文件操作工具,将PDF文件保存到指定目录
    输入:
        file_paths: 多个PDF文件的路径列表
    输出:
        bool: 是否保存成功
    """
    return NotImplementedError("子类必须实现此方法")

pdf_split(sys.argv[1])
