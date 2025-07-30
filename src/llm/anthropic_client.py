"""
Anthropic客户端实现

提供Anthropic Claude API的访问接口。
"""

import asyncio
import os
from typing import Dict, List, Optional
import anthropic
from .base import BaseLLMClient, LLMResponse


class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API客户端"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229", **kwargs):
        # 如果没有提供API密钥，尝试从环境变量获取
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set")
        
        super().__init__(api_key, model, **kwargs)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本响应"""
        # 保存提示词到文件
        self._save_prompt_to_file({
            "prompt": prompt,
            "kwargs": {**self.kwargs, **kwargs}
        }, "generate")
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4000),
                messages=[{"role": "user", "content": prompt}],
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                } if response.usage else None,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            raise Exception(f"Anthropic API调用失败: {str(e)}")
    
    async def generate_with_system_prompt(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        **kwargs
    ) -> LLMResponse:
        """使用系统提示词生成响应"""
        # 保存提示词到文件
        self._save_prompt_to_file({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "kwargs": {**self.kwargs, **kwargs}
        }, "generate_with_system_prompt")
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4000),
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                } if response.usage else None,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            raise Exception(f"Anthropic API调用失败: {str(e)}")
    
    async def generate_with_messages(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> LLMResponse:
        """使用消息列表生成响应"""
        # 保存提示词到文件
        self._save_prompt_to_file({
            "messages": messages,
            "kwargs": {**self.kwargs, **kwargs}
        }, "generate_with_messages")
        
        try:
            # 将消息格式转换为Anthropic格式
            anthropic_messages = []
            system_prompt = None
            
            for msg in messages:
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    anthropic_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 4000),
                messages=anthropic_messages,
                system=system_prompt,
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                } if response.usage else None,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            raise Exception(f"Anthropic API调用失败: {str(e)}") 