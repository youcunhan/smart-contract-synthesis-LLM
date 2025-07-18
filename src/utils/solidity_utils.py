"""
Solidity工具函数

提供Solidity代码相关的工具函数。
"""

import re
from typing import List, Dict, Optional, Tuple


class SolidityUtils:
    """Solidity工具类"""
    
    @staticmethod
    def extract_contract_name(code: str) -> Optional[str]:
        """从Solidity代码中提取合约名称"""
        pattern = r'contract\s+(\w+)'
        match = re.search(pattern, code)
        return match.group(1) if match else None
    
    @staticmethod
    def extract_functions(code: str) -> List[Dict[str, str]]:
        """从Solidity代码中提取函数信息"""
        functions = []
        pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*(?:returns\s*\(([^)]*)\))?\s*(?:public|private|internal|external)?'
        
        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            func_name = match.group(1)
            params = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None
            
            functions.append({
                "name": func_name,
                "parameters": params,
                "return_type": return_type
            })
        
        return functions
    
    @staticmethod
    def extract_state_variables(code: str) -> List[str]:
        """从Solidity代码中提取状态变量"""
        variables = []
        # 匹配状态变量声明
        pattern = r'(?:public|private|internal)?\s*(?:uint|int|bool|address|string|bytes|mapping)\s+(?:\d+)?\s*\w+\s*;'
        
        matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            variables.append(match.group(0).strip())
        
        return variables
    
    @staticmethod
    def extract_events(code: str) -> List[str]:
        """从Solidity代码中提取事件定义"""
        events = []
        pattern = r'event\s+\w+\s*\([^)]*\);'
        
        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            events.append(match.group(0).strip())
        
        return events
    
    @staticmethod
    def extract_structs(code: str) -> List[str]:
        """从Solidity代码中提取结构体定义"""
        structs = []
        pattern = r'struct\s+\w+\s*\{[^}]*\}'
        
        matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
        for match in matches:
            structs.append(match.group(0).strip())
        
        return structs
    
    @staticmethod
    def validate_solidity_syntax(code: str) -> Tuple[bool, List[str]]:
        """验证Solidity语法"""
        errors = []
        
        # 检查pragma声明
        if not re.search(r'pragma\s+solidity', code, re.IGNORECASE):
            errors.append("缺少pragma solidity声明")
        
        # 检查合约定义
        if not re.search(r'contract\s+\w+', code):
            errors.append("缺少合约定义")
        
        # 检查括号匹配
        if code.count('{') != code.count('}'):
            errors.append("括号不匹配")
        
        # 检查分号
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.endswith(';') and not line.endswith('{') and not line.endswith('}') and not line.startswith('//'):
                # 检查是否是函数声明、事件声明等不需要分号的行
                if not any(keyword in line for keyword in ['function', 'event', 'struct', 'contract', 'pragma', 'import', 'modifier']):
                    errors.append(f"第{i}行可能缺少分号: {line}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def format_solidity_code(code: str) -> str:
        """格式化Solidity代码"""
        # 基本的格式化规则
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
                continue
            
            # 减少缩进的情况
            if line.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # 添加缩进
            formatted_line = '    ' * indent_level + line
            formatted_lines.append(formatted_line)
            
            # 增加缩进的情况
            if line.endswith('{'):
                indent_level += 1
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def extract_imports(code: str) -> List[str]:
        """从Solidity代码中提取导入语句"""
        imports = []
        pattern = r'import\s+[\'"][^\'"]+[\'"];'
        
        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            imports.append(match.group(0).strip())
        
        return imports
    
    @staticmethod
    def add_spdx_license(code: str, license_type: str = "MIT") -> str:
        """添加SPDX许可证标识"""
        spdx_line = f"// SPDX-License-Identifier: {license_type}\n"
        
        # 如果已经有SPDX标识，替换它
        if "// SPDX-License-Identifier:" in code:
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if "// SPDX-License-Identifier:" in line:
                    lines[i] = spdx_line
                    break
            return '\n'.join(lines)
        else:
            return spdx_line + code
    
    @staticmethod
    def extract_function_body(code: str, function_name: str) -> Optional[str]:
        """提取指定函数的主体代码"""
        pattern = rf'function\s+{re.escape(function_name)}\s*\([^)]*\)[^{{]*\{{([^}}]*(?:{{[^}}]*}}[^}}]*)*)}}'
        
        match = re.search(pattern, code, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    @staticmethod
    def count_gas_estimation(code: str) -> Dict[str, int]:
        """估算gas使用情况"""
        gas_estimates = {
            "storage_operations": 0,
            "memory_operations": 0,
            "external_calls": 0,
            "complex_operations": 0
        }
        
        # 存储操作
        storage_patterns = [
            r'\.storage\b',
            r'storage\s+\w+',
            r'\w+\.\w+\s*='
        ]
        
        # 内存操作
        memory_patterns = [
            r'\.memory\b',
            r'memory\s+\w+',
            r'new\s+\w+'
        ]
        
        # 外部调用
        external_patterns = [
            r'\.call\(',
            r'\.delegatecall\(',
            r'\.staticcall\(',
            r'\.transfer\(',
            r'\.send\('
        ]
        
        # 复杂操作
        complex_patterns = [
            r'for\s*\(',
            r'while\s*\(',
            r'require\(',
            r'assert\(',
            r'revert\('
        ]
        
        for pattern in storage_patterns:
            gas_estimates["storage_operations"] += len(re.findall(pattern, code))
        
        for pattern in memory_patterns:
            gas_estimates["memory_operations"] += len(re.findall(pattern, code))
        
        for pattern in external_patterns:
            gas_estimates["external_calls"] += len(re.findall(pattern, code))
        
        for pattern in complex_patterns:
            gas_estimates["complex_operations"] += len(re.findall(pattern, code))
        
        return gas_estimates 