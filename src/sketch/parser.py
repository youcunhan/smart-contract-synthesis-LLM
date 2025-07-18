"""
Solidity Sketch解析器

解析文本格式的sketch文件，提取合约结构、交易和规范信息。
"""

import re
from typing import List, Optional
from pathlib import Path
from .models import Sketch, Transaction, Specification, GlobalSpec


class SketchParser:
    """Solidity Sketch解析器"""
    
    def __init__(self):
        self.current_section = None
        self.current_transaction = None
    
    def parse_file(self, file_path: str) -> Sketch:
        """解析sketch文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Sketch:
        """解析sketch内容"""
        lines = content.split('\n')
        
        # 初始化sketch
        sketch = Sketch(contract_name="")
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # 解析合约名称
            if line.startswith('contract '):
                match = re.match(r'contract\s+(\w+)', line)
                if match:
                    sketch.contract_name = match.group(1)
                continue
            
            # 解析结构体
            if line.startswith('struct '):
                sketch.structs.append(line)
                continue
            
            # 解析事件
            if line.startswith('event '):
                sketch.events.append(line)
                continue
            
            # 解析状态变量
            if self._is_state_variable(line):
                sketch.state_variables.append(line)
                continue
            
            # 解析函数
            if self._is_function_declaration(line):
                self._parse_function(line, sketch)
                continue
            
            # 解析函数内容
            if self.current_transaction and '{' in line:
                self._parse_function_content(line, sketch)
                continue
            
            # 解析规范
            if line.startswith('//@'):
                self._parse_specification(line, sketch)
                continue
        
        return sketch
    
    def _is_state_variable(self, line: str) -> bool:
        """判断是否为状态变量"""
        # 简单的状态变量识别规则
        state_var_patterns = [
            r'^\s*(uint|int|bool|address|string|bytes|mapping)\s+\w+',
            r'^\s*(uint|int|bool|address|string|bytes|mapping)\s*\[\s*\]\s+\w+',
        ]
        
        for pattern in state_var_patterns:
            if re.match(pattern, line):
                return True
        return False
    
    def _is_function_declaration(self, line: str) -> bool:
        """判断是否为函数声明"""
        return re.match(r'^\s*function\s+\w+\s*\(', line) is not None
    
    def _parse_function(self, line: str, sketch: Sketch):
        """解析函数声明"""
        # 提取函数名
        match = re.match(r'^\s*function\s+(\w+)\s*\(', line)
        if not match:
            return
        
        func_name = match.group(1)
        
        # 提取参数
        params_match = re.search(r'\(([^)]*)\)', line)
        parameters = []
        if params_match:
            params_str = params_match.group(1).strip()
            if params_str:
                parameters = [p.strip() for p in params_str.split(',')]
        
        # 提取返回类型
        return_type = None
        if 'returns' in line:
            returns_match = re.search(r'returns\s*\(([^)]*)\)', line)
            if returns_match:
                return_type = returns_match.group(1).strip()
        
        # 提取可见性
        visibility = "public"
        if "private" in line:
            visibility = "private"
        elif "internal" in line:
            visibility = "internal"
        elif "external" in line:
            visibility = "external"
        
        # 创建交易对象
        self.current_transaction = Transaction(
            name=func_name,
            parameters=parameters,
            return_type=return_type,
            visibility=visibility
        )
        
        sketch.transactions.append(self.current_transaction)
    
    def _parse_function_content(self, line: str, sketch: Sketch):
        """解析函数内容"""
        if not self.current_transaction:
            return
        
        if not hasattr(self.current_transaction, 'sketch_code'):
            self.current_transaction.sketch_code = ""
        
        self.current_transaction.sketch_code += line + "\n"
    
    def _parse_specification(self, line: str, sketch: Sketch):
        """解析规范"""
        # 移除注释符号
        spec_line = line.replace('//@', '').strip()
        
        # 解析全局规范
        if spec_line.startswith('global'):
            self._parse_global_spec(spec_line, sketch)
        # 解析函数规范
        elif spec_line.startswith('function'):
            self._parse_function_spec(spec_line, sketch)
    
    def _parse_global_spec(self, line: str, sketch: Sketch):
        """解析全局规范"""
        if 'invariant' in line:
            invariant = line.split('invariant')[1].strip()
            sketch.global_spec.invariants.append(invariant)
        elif 'constraint' in line:
            constraint = line.split('constraint')[1].strip()
            sketch.global_spec.constraints.append(constraint)
        elif 'assumption' in line:
            assumption = line.split('assumption')[1].strip()
            sketch.global_spec.assumptions.append(assumption)
    
    def _parse_function_spec(self, line: str, sketch: Sketch):
        """解析函数规范"""
        # 提取函数名
        match = re.search(r'function\s+(\w+)', line)
        if not match:
            return
        
        func_name = match.group(1)
        transaction = sketch.get_transaction_by_name(func_name)
        if not transaction:
            return
        
        # 解析前置条件
        if 'pre:' in line:
            pre_condition = line.split('pre:')[1].split('post:')[0].strip()
            if not transaction.spec:
                transaction.spec = Specification(pre_condition="", post_condition="")
            transaction.spec.pre_condition = pre_condition
        
        # 解析后置条件
        if 'post:' in line:
            post_condition = line.split('post:')[1].strip()
            if not transaction.spec:
                transaction.spec = Specification(pre_condition="", post_condition="")
            transaction.spec.post_condition = post_condition 