"""
Solidity Sketch验证器

验证sketch的完整性和一致性。
"""

from typing import List, Dict, Tuple
from .models import Sketch, Transaction, Specification


class SketchValidator:
    """Solidity Sketch验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, sketch: Sketch) -> Tuple[bool, List[str], List[str]]:
        """验证sketch"""
        self.errors = []
        self.warnings = []
        
        # 基本验证
        self._validate_basic_structure(sketch)
        
        # 交易验证
        self._validate_transactions(sketch)
        
        # 规范验证
        self._validate_specifications(sketch)
        
        # 一致性验证
        self._validate_consistency(sketch)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_basic_structure(self, sketch: Sketch):
        """验证基本结构"""
        # 检查合约名称
        if not sketch.contract_name:
            self.errors.append("合约名称不能为空")
        elif not sketch.contract_name[0].isupper():
            self.warnings.append("合约名称应该以大写字母开头")
        
        # 检查交易列表
        if not sketch.transactions:
            self.errors.append("合约必须包含至少一个交易")
    
    def _validate_transactions(self, sketch: Sketch):
        """验证交易"""
        transaction_names = []
        
        for i, transaction in enumerate(sketch.transactions):
            # 检查交易名称
            if not transaction.name:
                self.errors.append(f"交易 {i+1}: 名称不能为空")
                continue
            
            # 检查名称唯一性
            if transaction.name in transaction_names:
                self.errors.append(f"交易名称重复: {transaction.name}")
            else:
                transaction_names.append(transaction.name)
            
            # 检查参数格式
            self._validate_parameters(transaction, i)
            
            # 检查可见性
            if transaction.visibility not in ["public", "private", "internal", "external"]:
                self.errors.append(f"交易 {transaction.name}: 无效的可见性 {transaction.visibility}")
    
    def _validate_parameters(self, transaction: Transaction, index: int):
        """验证参数"""
        for j, param in enumerate(transaction.parameters):
            if not param.strip():
                self.errors.append(f"交易 {transaction.name}: 参数 {j+1} 不能为空")
                continue
            
            # 检查参数格式 (类型 名称)
            parts = param.strip().split()
            if len(parts) < 2:
                self.errors.append(f"交易 {transaction.name}: 参数格式错误: {param}")
    
    def _validate_specifications(self, sketch: Sketch):
        """验证规范"""
        # 验证全局规范
        self._validate_global_spec(sketch.global_spec)
        
        # 验证函数规范
        for transaction in sketch.transactions:
            if transaction.spec:
                self._validate_function_spec(transaction)
    
    def _validate_global_spec(self, global_spec):
        """验证全局规范"""
        # 检查不变量
        for i, invariant in enumerate(global_spec.invariants):
            if not invariant.strip():
                self.errors.append(f"全局不变量 {i+1}: 不能为空")
        
        # 检查约束条件
        for i, constraint in enumerate(global_spec.constraints):
            if not constraint.strip():
                self.errors.append(f"全局约束 {i+1}: 不能为空")
    
    def _validate_function_spec(self, transaction: Transaction):
        """验证函数规范"""
        spec = transaction.spec
        
        # 检查前置条件
        if not spec.pre_condition.strip():
            self.warnings.append(f"交易 {transaction.name}: 前置条件为空")
        
        # 检查后置条件
        if not spec.post_condition.strip():
            self.warnings.append(f"交易 {transaction.name}: 后置条件为空")
        
        # 检查条件语法
        self._validate_condition_syntax(spec.pre_condition, f"交易 {transaction.name} 前置条件")
        self._validate_condition_syntax(spec.post_condition, f"交易 {transaction.name} 后置条件")
    
    def _validate_condition_syntax(self, condition: str, context: str):
        """验证条件语法"""
        if not condition.strip():
            return
        
        # 检查基本语法错误
        condition = condition.strip()
        
        # 检查括号匹配
        if condition.count('(') != condition.count(')'):
            self.errors.append(f"{context}: 括号不匹配")
        
        # 检查逻辑操作符
        logical_ops = ['&&', '||', '==', '!=', '<=', '>=', '<', '>']
        for op in logical_ops:
            if op in condition and not self._is_valid_logical_expression(condition, op):
                self.warnings.append(f"{context}: 逻辑操作符 {op} 使用可能不正确")
    
    def _is_valid_logical_expression(self, condition: str, op: str) -> bool:
        """检查逻辑表达式是否有效"""
        # 简单的逻辑表达式验证
        parts = condition.split(op)
        if len(parts) < 2:
            return False
        
        for part in parts:
            if not part.strip():
                return False
        
        return True
    
    def _validate_consistency(self, sketch: Sketch):
        """验证一致性"""
        # 检查状态变量在规范中的使用
        state_var_names = self._extract_state_var_names(sketch.state_variables)
        
        for transaction in sketch.transactions:
            if transaction.spec:
                self._validate_var_usage_in_spec(transaction.spec, state_var_names, transaction.name)
    
    def _extract_state_var_names(self, state_variables: List[str]) -> List[str]:
        """提取状态变量名称"""
        names = []
        for var in state_variables:
            # 简单的变量名提取
            parts = var.split()
            if len(parts) >= 2:
                # 取最后一个部分作为变量名
                var_name = parts[-1].rstrip(';')
                names.append(var_name)
        return names
    
    def _validate_var_usage_in_spec(self, spec: Specification, state_vars: List[str], func_name: str):
        """验证规范中的变量使用"""
        # 检查前置条件中的变量使用
        for var in state_vars:
            if var in spec.pre_condition and not self._is_valid_var_usage(spec.pre_condition, var):
                self.warnings.append(f"交易 {func_name}: 前置条件中变量 {var} 使用可能不正确")
        
        # 检查后置条件中的变量使用
        for var in state_vars:
            if var in spec.post_condition and not self._is_valid_var_usage(spec.post_condition, var):
                self.warnings.append(f"交易 {func_name}: 后置条件中变量 {var} 使用可能不正确")
    
    def _is_valid_var_usage(self, condition: str, var_name: str) -> bool:
        """检查变量使用是否有效"""
        # 简单的变量使用验证
        # 检查变量是否在有效的上下文中使用
        if f"{var_name}." in condition:  # 结构体成员访问
            return True
        if f" {var_name} " in condition:  # 独立变量
            return True
        if condition.startswith(var_name) or condition.endswith(var_name):  # 开头或结尾
            return True
        
        return False 