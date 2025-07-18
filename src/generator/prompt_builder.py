"""
提示词构建器

构建用于LLM的输入提示，包含sketch、规范和库信息。
"""

from typing import List, Dict, Any
from ..sketch.models import Sketch, Transaction
from ..libraries.docs_manager import LibraryDocsManager


class PromptBuilder:
    """提示词构建器"""
    
    def __init__(self, library_manager: LibraryDocsManager):
        self.library_manager = library_manager
    
    def build_generation_prompt(self, sketch: Sketch) -> str:
        """构建代码生成提示词"""
        prompt = self._build_system_prompt()
        prompt += "\n\n"
        prompt += self._build_sketch_section(sketch)
        prompt += "\n\n"
        prompt += self._build_specification_section(sketch)
        prompt += "\n\n"
        prompt += self._build_library_section(sketch)
        prompt += "\n\n"
        prompt += self._build_instruction_section()
        
        return prompt
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个专业的Solidity智能合约开发专家。你的任务是根据提供的合约草图(sketch)和规范(specification)生成完整、安全、高效的Solidity智能合约代码。

## 你的职责：
1. 分析合约草图，理解合约的结构和功能
2. 根据规范要求实现合约逻辑
3. 确保代码符合Solidity最佳实践和安全标准
4. 使用推荐的库来增强合约功能
5. 生成可以直接编译和部署的完整合约代码

## 代码要求：
- 使用Solidity 0.8.0或更高版本
- 遵循Solidity编码规范
- 包含适当的错误处理和访问控制
- 优化gas使用
- 添加必要的注释说明
- 确保代码的可读性和可维护性"""
    
    def _build_sketch_section(self, sketch: Sketch) -> str:
        """构建sketch部分"""
        section = "## 合约草图\n\n"
        section += f"合约名称: {sketch.contract_name}\n\n"
        
        # 导入语句
        if sketch.imports:
            section += "### 导入语句\n"
            for imp in sketch.imports:
                section += f"```solidity\n{imp}\n```\n"
            section += "\n"
        
        # 状态变量
        if sketch.state_variables:
            section += "### 状态变量\n"
            for var in sketch.state_variables:
                section += f"```solidity\n{var}\n```\n"
            section += "\n"
        
        # 结构体
        if sketch.structs:
            section += "### 结构体定义\n"
            for struct in sketch.structs:
                section += f"```solidity\n{struct}\n```\n"
            section += "\n"
        
        # 事件
        if sketch.events:
            section += "### 事件定义\n"
            for event in sketch.events:
                section += f"```solidity\n{event}\n```\n"
            section += "\n"
        
        # 函数
        if sketch.transactions:
            section += "### 函数定义\n"
            for tx in sketch.transactions:
                section += f"#### {tx.name}\n"
                section += f"```solidity\n"
                section += f"function {tx.name}("
                if tx.parameters:
                    section += ", ".join(tx.parameters)
                section += f") {tx.visibility}"
                if tx.return_type:
                    section += f" returns ({tx.return_type})"
                section += "\n```\n"
                
                if tx.sketch_code:
                    section += f"草图代码:\n```solidity\n{tx.sketch_code}\n```\n"
                section += "\n"
        
        return section
    
    def _build_specification_section(self, sketch: Sketch) -> str:
        """构建规范部分"""
        section = "## 合约规范\n\n"
        
        # 全局规范
        if sketch.global_spec.invariants or sketch.global_spec.constraints or sketch.global_spec.assumptions:
            section += "### 全局规范\n\n"
            
            if sketch.global_spec.invariants:
                section += "**不变量:**\n"
                for invariant in sketch.global_spec.invariants:
                    section += f"- {invariant}\n"
                section += "\n"
            
            if sketch.global_spec.constraints:
                section += "**约束条件:**\n"
                for constraint in sketch.global_spec.constraints:
                    section += f"- {constraint}\n"
                section += "\n"
            
            if sketch.global_spec.assumptions:
                section += "**假设条件:**\n"
                for assumption in sketch.global_spec.assumptions:
                    section += f"- {assumption}\n"
                section += "\n"
        
        # 函数规范
        function_specs = [tx for tx in sketch.transactions if tx.spec]
        if function_specs:
            section += "### 函数规范\n\n"
            for tx in function_specs:
                section += f"#### {tx.name}\n"
                if tx.spec and tx.spec.pre_condition:
                    section += f"**前置条件:** {tx.spec.pre_condition}\n"
                if tx.spec and tx.spec.post_condition:
                    section += f"**后置条件:** {tx.spec.post_condition}\n"
                if tx.spec and tx.spec.description:
                    section += f"**描述:** {tx.spec.description}\n"
                section += "\n"
        
        return section
    
    def _build_library_section(self, sketch: Sketch) -> str:
        """构建库推荐部分"""
        # 将sketch转换为字符串以提取关键词
        sketch_content = self._sketch_to_string(sketch)
        library_prompt = self.library_manager.generate_library_prompt(sketch_content)
        
        if library_prompt != "未找到相关的库推荐。":
            return f"## 库推荐\n\n{library_prompt}"
        else:
            return "## 库推荐\n\n根据合约需求，建议考虑使用以下常用库：\n\n- **OpenZeppelin**: 提供安全的合约组件和工具\n- **SafeMath**: 防止数学运算溢出\n- **Ownable**: 访问控制功能\n- **ReentrancyGuard**: 防止重入攻击"
    
    def _build_instruction_section(self) -> str:
        """构建指令部分"""
        return """## 生成要求

请根据上述信息生成完整的Solidity合约代码，要求：

1. **完整性**: 实现所有在草图中定义的函数和功能
2. **安全性**: 遵循安全最佳实践，防止常见漏洞
3. **规范性**: 确保代码符合Solidity编码规范
4. **可读性**: 添加适当的注释和文档
5. **效率**: 优化gas使用和性能

## 输出格式

请直接输出完整的Solidity合约代码，包括：
- SPDX许可证标识
- 版本声明
- 导入语句
- 完整的合约代码
- 适当的注释

代码应该可以直接编译和部署。"""
    
    def _sketch_to_string(self, sketch: Sketch) -> str:
        """将sketch转换为字符串"""
        content = f"contract {sketch.contract_name} {{\n"
        
        # 添加状态变量
        for var in sketch.state_variables:
            content += f"    {var}\n"
        
        # 添加结构体
        for struct in sketch.structs:
            content += f"    {struct}\n"
        
        # 添加事件
        for event in sketch.events:
            content += f"    {event}\n"
        
        # 添加函数
        for tx in sketch.transactions:
            content += f"    function {tx.name}("
            if tx.parameters:
                content += ", ".join(tx.parameters)
            content += f") {tx.visibility}"
            if tx.return_type:
                content += f" returns ({tx.return_type})"
            content += " {\n"
            if tx.sketch_code:
                content += f"        {tx.sketch_code}\n"
            content += "    }\n"
        
        content += "}"
        return content
    
    def build_validation_prompt(self, generated_code: str, sketch: Sketch) -> str:
        """构建验证提示词"""
        prompt = """你是一个Solidity代码验证专家。请验证生成的合约代码是否满足原始草图的要求。

## 验证任务

请检查生成的代码是否：

1. **功能完整性**: 实现了所有在草图中定义的函数
2. **规范符合性**: 满足所有前置条件和后置条件
3. **安全性**: 没有明显的安全漏洞
4. **正确性**: 代码语法正确，逻辑合理

## 生成的代码

```solidity
{generated_code}
```

## 原始草图

{sketch_summary}

## 验证结果

请提供详细的验证报告，包括：
- 功能完整性检查
- 规范符合性检查
- 安全性检查
- 发现的问题和建议
- 总体评价

"""
        
        sketch_summary = self._build_sketch_summary(sketch)
        return prompt.format(generated_code=generated_code, sketch_summary=sketch_summary)
    
    def _build_sketch_summary(self, sketch: Sketch) -> str:
        """构建草图摘要"""
        summary = f"合约名称: {sketch.contract_name}\n\n"
        
        summary += "函数列表:\n"
        for tx in sketch.transactions:
            summary += f"- {tx.name}("
            if tx.parameters:
                summary += ", ".join(tx.parameters)
            summary += f") {tx.visibility}\n"
        
        summary += "\n规范要求:\n"
        for tx in sketch.transactions:
            if tx.spec:
                summary += f"- {tx.name}: pre={tx.spec.pre_condition}, post={tx.spec.post_condition}\n"
        
        return summary 