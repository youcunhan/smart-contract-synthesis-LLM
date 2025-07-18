#!/usr/bin/env python3
"""
Smart Contract Synthesis LLM 使用示例

展示如何使用这个项目来生成智能合约。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.llm import OpenAIClient
from src.generator import ContractGenerator
from src.sketch import SketchParser, SketchValidator
from src.libraries import LibraryDocsManager
from src.utils import FileUtils


async def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=== 示例1: 基本使用 ===")
    
    # 1. 设置API密钥（请替换为你的实际API密钥）
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    
    # 2. 创建LLM客户端
    llm_client = OpenAIClient(api_key=api_key, model="gpt-4")
    
    # 3. 创建合约生成器
    generator = ContractGenerator(llm_client)
    
    # 4. 从sketch文件生成合约
    sketch_file = "src/sketch/examples/sheep_farm_sketch.txt"
    output_file = "generated_contracts/SheepFarm.sol"
    
    try:
        contract_code = await generator.generate_from_file(sketch_file, output_file)
        print(f"✅ 合约生成成功！")
        print(f"合约代码长度: {len(contract_code)} 字符")
        print(f"输出文件: {output_file}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")


async def example_2_sketch_validation():
    """示例2: Sketch验证"""
    print("\n=== 示例2: Sketch验证 ===")
    
    # 创建解析器和验证器
    parser = SketchParser()
    validator = SketchValidator()
    
    # 解析sketch文件
    sketch_file = "src/sketch/examples/sheep_farm_sketch.txt"
    sketch = parser.parse_file(sketch_file)
    
    # 验证sketch
    is_valid, errors, warnings = validator.validate(sketch)
    
    print(f"合约名称: {sketch.contract_name}")
    print(f"函数数量: {len(sketch.transactions)}")
    print(f"状态变量数量: {len(sketch.state_variables)}")
    print(f"验证结果: {'✅ 通过' if is_valid else '❌ 失败'}")
    
    if errors:
        print("错误:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("警告:")
        for warning in warnings:
            print(f"  - {warning}")


def example_3_library_management():
    """示例3: 库管理"""
    print("\n=== 示例3: 库管理 ===")
    
    # 创建库管理器
    library_manager = LibraryDocsManager()
    
    # 列出所有可用库
    libraries = library_manager.get_all_libraries()
    print(f"可用库数量: {len(libraries)}")
    
    # 显示OpenZeppelin库信息
    openzeppelin = library_manager.get_library("openzeppelin")
    if openzeppelin:
        print(f"\n📚 {openzeppelin.name}")
        print(f"描述: {openzeppelin.description}")
        print("主要功能:")
        for func in openzeppelin.functions[:3]:
            print(f"  - {func['name']}: {func['description']}")


async def example_4_custom_generation():
    """示例4: 自定义生成"""
    print("\n=== 示例4: 自定义生成 ===")
    
    # 创建自定义sketch
    custom_sketch_content = """
    contract CustomToken {
        string public name;
        uint256 public totalSupply;
        mapping(address => uint256) public balanceOf;
        
        event Transfer(address indexed from, address indexed to, uint256 value);
        
        //@global invariant: totalSupply >= 0
        
        function mint(address to, uint256 amount) public {
            //@function mint pre: to != address(0) && amount > 0
            //@function mint post: balanceOf[to] == old(balanceOf[to]) + amount
            require(to != address(0), "Invalid recipient");
            require(amount > 0, "Amount must be positive");
            
            balanceOf[to] += amount;
            totalSupply += amount;
            emit Transfer(address(0), to, amount);
        }
        
        function transfer(address to, uint256 amount) public returns (bool) {
            //@function transfer pre: to != address(0) && balanceOf[msg.sender] >= amount
            //@function transfer post: balanceOf[msg.sender] == old(balanceOf[msg.sender]) - amount
            require(to != address(0), "Invalid recipient");
            require(balanceOf[msg.sender] >= amount, "Insufficient balance");
            
            balanceOf[msg.sender] -= amount;
            balanceOf[to] += amount;
            emit Transfer(msg.sender, to, amount);
            return true;
        }
    }
    """
    
    # 保存自定义sketch
    custom_sketch_file = "examples/custom_token_sketch.txt"
    FileUtils.write_text_file(custom_sketch_file, custom_sketch_content)
    
    # 设置API密钥
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    llm_client = OpenAIClient(api_key=api_key, model="gpt-4")
    generator = ContractGenerator(llm_client)
    
    try:
        # 生成合约
        contract_code = await generator.generate_from_file(custom_sketch_file, "generated_contracts/CustomToken.sol")
        print("✅ 自定义合约生成成功！")
        
        # 分析生成的代码
        from src.utils import SolidityUtils
        functions = SolidityUtils.extract_functions(contract_code)
        print(f"生成的函数数量: {len(functions)}")
        for func in functions:
            print(f"  - {func['name']}")
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")


def example_5_utility_functions():
    """示例5: 工具函数使用"""
    print("\n=== 示例5: 工具函数使用 ===")
    
    # 读取生成的合约文件
    contract_file = "generated_contracts/SheepFarm.sol"
    if FileUtils.file_exists(contract_file):
        contract_code = FileUtils.read_text_file(contract_file)
        
        # 使用Solidity工具函数分析代码
        from src.utils import SolidityUtils
        
        # 提取合约名称
        contract_name = SolidityUtils.extract_contract_name(contract_code)
        print(f"合约名称: {contract_name}")
        
        # 提取函数信息
        functions = SolidityUtils.extract_functions(contract_code)
        print(f"函数数量: {len(functions)}")
        
        # 提取状态变量
        state_vars = SolidityUtils.extract_state_variables(contract_code)
        print(f"状态变量数量: {len(state_vars)}")
        
        # 验证语法
        is_valid, errors = SolidityUtils.validate_solidity_syntax(contract_code)
        print(f"语法验证: {'✅ 通过' if is_valid else '❌ 失败'}")
        
        # 估算gas使用
        gas_estimates = SolidityUtils.count_gas_estimation(contract_code)
        print("Gas估算:")
        for operation, count in gas_estimates.items():
            print(f"  - {operation}: {count}")
    else:
        print("❌ 合约文件不存在，请先生成合约")


async def main():
    """主函数"""
    print("🚀 Smart Contract Synthesis LLM 使用示例")
    print("=" * 50)
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置OPENAI_API_KEY环境变量")
        print("请设置环境变量或在代码中直接设置API密钥")
        print("示例: export OPENAI_API_KEY='your-api-key-here'")
        print()
    
    # 运行示例
    await example_1_basic_usage()
    await example_2_sketch_validation()
    example_3_library_management()
    await example_4_custom_generation()
    example_5_utility_functions()
    
    print("\n" + "=" * 50)
    print("✅ 所有示例运行完成！")
    print("\n📝 使用提示:")
    print("1. 确保设置了正确的API密钥")
    print("2. 检查生成的合约文件在 generated_contracts/ 目录中")
    print("3. 可以使用 solc 编译器验证生成的合约")
    print("4. 建议在部署前进行安全审计")


if __name__ == "__main__":
    asyncio.run(main()) 