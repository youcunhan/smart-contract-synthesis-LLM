"""
OpenAI客户端实现

提供OpenAI API的访问接口。
"""

import asyncio
import os
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from .base import BaseLLMClient, LLMResponse


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4", **kwargs):
        # 如果没有提供API密钥，尝试从环境变量获取
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not provided and OPENAI_API_KEY environment variable not set")
        
        super().__init__(api_key, model, **kwargs)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本响应"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **{**self.kwargs, **kwargs}
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    async def generate_with_system_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        **kwargs
    ) -> LLMResponse:
        """使用系统提示词生成响应"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return await self.generate_with_messages(messages, **kwargs)
    
    async def generate_with_messages(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """使用消息列表生成响应"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **{**self.kwargs, **kwargs}
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}") 