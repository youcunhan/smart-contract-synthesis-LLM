"""
LLM基础接口类

定义所有LLM客户端必须实现的接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """LLM响应模型"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class BaseLLMClient(ABC):
    """LLM客户端基础类"""
    
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本响应"""
        pass
    
    @abstractmethod
    async def generate_with_system_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        **kwargs
    ) -> LLMResponse:
        """使用系统提示词生成响应"""
        pass
    
    @abstractmethod
    async def generate_with_messages(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """使用消息列表生成响应"""
        pass
    
    def validate_response(self, response: LLMResponse) -> bool:
        """验证响应是否有效"""
        return bool(response.content and response.content.strip()) 