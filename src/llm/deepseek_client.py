"""
DeepSeek客户端实现

提供DeepSeek API的访问接口。
"""

import asyncio
import os
import aiohttp
from typing import Dict, List, Optional
from .base import BaseLLMClient, LLMResponse


class DeepSeekClient(BaseLLMClient):
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str = None, model: str = "deepseek-chat", **kwargs):
        # 如果没有提供API密钥，尝试从环境变量获取
        if not api_key:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DeepSeek API key not provided and DEEPSEEK_API_KEY environment variable not set")
        
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.deepseek.com")
        self.timeout = kwargs.get("timeout", 60)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """生成文本响应"""
        messages = [{"role": "user", "content": prompt}]
        return await self.generate_with_messages(messages, **kwargs)
    
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
        url = f"{self.base_url}/v1/chat/completions"
        
        # 构建请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.kwargs.get("max_tokens", 4000)),
            "temperature": kwargs.get("temperature", self.kwargs.get("temperature", 0.1)),
            "stream": False
        }
        
        # 添加其他参数
        for key, value in kwargs.items():
            if key not in ["max_tokens", "temperature", "stream"]:
                data[key] = value
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"DeepSeek API错误 (状态码: {response.status}): {error_text}")
                    
                    result = await response.json()
                    
                    return LLMResponse(
                        content=result["choices"][0]["message"]["content"],
                        model=result["model"],
                        usage={
                            "prompt_tokens": result["usage"]["prompt_tokens"],
                            "completion_tokens": result["usage"]["completion_tokens"],
                            "total_tokens": result["usage"]["total_tokens"]
                        } if "usage" in result else None,
                        finish_reason=result["choices"][0]["finish_reason"]
                    )
        except aiohttp.ClientError as e:
            raise Exception(f"DeepSeek API网络错误: {str(e)}")
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    async def test_connection(self) -> bool:
        """测试API连接"""
        try:
            response = await self.generate("Hello", max_tokens=10)
            return bool(response.content)
        except Exception:
            return False 