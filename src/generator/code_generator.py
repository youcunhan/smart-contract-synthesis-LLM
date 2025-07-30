"""
代码生成器

使用LLM根据sketch和规范生成完整的Solidity合约代码。
"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from ..llm.base import BaseLLMClient
from ..sketch.models import Sketch
from ..sketch.parser import SketchParser
from ..sketch.validator import SketchValidator
from ..libraries.docs_manager import LibraryDocsManager
from .prompt_builder import PromptBuilder


class ContractGenerator:
    """合约代码生成器"""
    
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.library_manager = LibraryDocsManager()
        self.prompt_builder = PromptBuilder(self.library_manager)
        self.parser = SketchParser()
        self.validator = SketchValidator()
    
    async def generate_from_file(self, sketch_file: str, output_file: Optional[str] = None, library_names: Optional[list] = None) -> str:
        """Generate contract from file, optionally with specific libraries."""
        sketch = self.parser.parse_file(sketch_file)
        is_valid, errors, warnings = self.validator.validate(sketch)
        if not is_valid:
            raise ValueError(f"Sketch validation failed: {errors}")
        if warnings:
            print(f"Warning: {warnings}")
        contract_code = await self.generate_from_sketch(sketch, library_names=library_names)
        if output_file:
            self._save_contract(contract_code, output_file)
        return contract_code

    async def generate_from_sketch(self, sketch: Sketch, library_names: Optional[list] = None) -> str:
        """Generate contract from sketch object, optionally with specific libraries."""
        # Build prompt
        prompt = self.prompt_builder.build_generation_prompt(sketch, library_names=library_names)
        # Save prompt for debugging
        with open('promote.tmp', 'w', encoding='utf-8') as f:
            f.write(prompt)
        # Call LLM
        response = await self.llm_client.generate_with_system_prompt(
            system_prompt="You are a professional Solidity smart contract developer.",
            user_prompt=prompt,
            max_tokens=4000,
            temperature=0.1
        )
        generated_code = self._extract_solidity_code(response.content)
        validation_result = await self._validate_generated_code(generated_code, sketch)
        return generated_code
    
    def _extract_solidity_code(self, llm_response: str) -> str:
        """从LLM响应中提取Solidity代码"""
        # 查找代码块
        if "```solidity" in llm_response:
            start = llm_response.find("```solidity") + len("```solidity")
            end = llm_response.find("```", start)
            if end != -1:
                return llm_response[start:end].strip()
        
        # 如果没有找到代码块标记，尝试提取整个响应
        lines = llm_response.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            if line.strip().startswith('// SPDX-License-Identifier:') or line.strip().startswith('pragma solidity'):
                in_code = True
            
            if in_code:
                code_lines.append(line)
            
            # 如果遇到空行且已经收集了代码，可能代码结束
            if in_code and not line.strip() and len(code_lines) > 10:
                break
        
        return '\n'.join(code_lines).strip()
    
    async def _validate_generated_code(self, generated_code: str, sketch: Sketch) -> Dict[str, Any]:
        """验证生成的代码"""
        validation_prompt = self.prompt_builder.build_validation_prompt(generated_code, sketch)
        
        try:
            response = await self.llm_client.generate_with_system_prompt(
                system_prompt="你是一个Solidity代码验证专家。",
                user_prompt=validation_prompt,
                max_tokens=2000,
                temperature=0.1
            )
            
            return {
                "valid": True,
                "validation_report": response.content,
                "generated_code": generated_code
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "generated_code": generated_code
            }
    
    def _save_contract(self, contract_code: str, output_file: str):
        """保存合约代码到文件"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(contract_code)
        
        print(f"合约已保存到: {output_path}")
    
    async def generate_with_retry(self, sketch: Sketch, max_retries: int = 3) -> str:
        """带重试的代码生成"""
        for attempt in range(max_retries):
            try:
                contract_code = await self.generate_from_sketch(sketch)
                
                # 基本验证
                if self._is_valid_solidity_code(contract_code):
                    return contract_code
                else:
                    print(f"尝试 {attempt + 1}: 生成的代码格式不正确，重试...")
                    
            except Exception as e:
                print(f"尝试 {attempt + 1} 失败: {e}")
                if attempt == max_retries - 1:
                    raise e
        
        raise Exception("代码生成失败，已达到最大重试次数")
    
    def _is_valid_solidity_code(self, code: str) -> bool:
        """检查生成的代码是否为有效的Solidity代码"""
        if not code or len(code.strip()) < 50:
            return False
        
        # 检查基本结构
        required_elements = [
            "pragma solidity",
            "contract",
            "{",
            "}"
        ]
        
        code_lower = code.lower()
        for element in required_elements:
            if element not in code_lower:
                return False
        
        return True
    
    async def generate_with_custom_prompt(self, sketch: Sketch, custom_prompt: str) -> str:
        """使用自定义提示词生成代码"""
        # 构建基础提示词
        base_prompt = self.prompt_builder.build_generation_prompt(sketch)
        
        # 添加自定义提示词
        full_prompt = base_prompt + "\n\n## 额外要求\n\n" + custom_prompt
        
        # 调用LLM
        response = await self.llm_client.generate_with_system_prompt(
            system_prompt="你是一个专业的Solidity智能合约开发专家。",
            user_prompt=full_prompt,
            max_tokens=4000,
            temperature=0.1
        )
        
        return self._extract_solidity_code(response.content)
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """获取生成统计信息"""
        return {
            "libraries_available": len(self.library_manager.get_all_libraries()),
            "supported_llm_providers": ["openai", "anthropic"],
            "max_tokens": 4000,
            "temperature": 0.1
        } 