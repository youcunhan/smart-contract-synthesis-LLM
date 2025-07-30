"""
LLM基础接口类

定义所有LLM客户端必须实现的接口。
"""

import os
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
    
    def _save_prompt_to_file(self, prompt_data: Dict[str, Any], method_name: str = "generate"):
        """保存提示词到临时文件"""
        try:
            prompt_content = f"Method: {method_name}\n"
            prompt_content += f"Model: {self.model}\n"
            prompt_content += f"Timestamp: {__import__('datetime').datetime.now().isoformat()}\n"
            prompt_content += "=" * 50 + "\n\n"
            
            if method_name == "generate":
                prompt_content += f"Prompt:\n{prompt_data.get('prompt', '')}\n"
            elif method_name == "generate_with_system_prompt":
                prompt_content += f"System Prompt:\n{prompt_data.get('system_prompt', '')}\n\n"
                prompt_content += f"User Prompt:\n{prompt_data.get('user_prompt', '')}\n"
            elif method_name == "generate_with_messages":
                prompt_content += "Messages:\n"
                for i, msg in enumerate(prompt_data.get('messages', [])):
                    prompt_content += f"[{i+1}] {msg.get('role', 'unknown')}: {msg.get('content', '')}\n"
            
            prompt_content += "\n" + "=" * 50 + "\n"
            prompt_content += f"Additional kwargs: {prompt_data.get('kwargs', {})}\n"
            
            # 保存到prompt.tmp文件
            with open("prompt.tmp", "w", encoding="utf-8") as f:
                f.write(prompt_content)
            
        except Exception as e:
            # 如果保存失败，不影响主要功能
            print(f"Warning: Failed to save prompt to file: {e}")
    
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