#!/usr/bin/env python3
"""
DeepSeek使用示例

展示如何使用DeepSeek API生成智能合约。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 直接导入模块
sys.path.insert(0, str(project_root))
from src.llm import DeepSeekClient
from src.generator import ContractGenerator
from src.sketch import SketchParser, SketchValidator
from src.utils import FileUtils


async def example_deepseek_contract_generation():
    """示例：使用DeepSeek生成智能合约"""
    print("=== DeepSeek智能合约生成示例 ===\n")
    
    # 1. 配置DeepSeek客户端
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
    
    if api_key == "your-deepseek-api-key-here":
        print("❌ 请设置DEEPSEEK_API_KEY环境变量或在config/config.yaml中配置API密钥")
        return
    
    # 创建DeepSeek客户端
    client = DeepSeekClient(
        api_key=api_key,
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        timeout=60
    )
    
    # 2. 创建合约生成器
    generator = ContractGenerator(client)
    
    # 3. 定义合约草图
    contract_sketch = """
contract ERC20Token {
    // State variables
    string public name;
    string public symbol;
    uint8 public decimals;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    
    // Global specifications
    //@global invariant: totalSupply >= 0
    //@global constraint: balanceOf[address] >= 0
    
    // Constructor
    function constructor(string memory _name, string memory _symbol, uint8 _decimals, uint256 _initialSupply) {
        //@function constructor pre: _initialSupply > 0 && _decimals <= 18
        //@function constructor post: name == _name && symbol == _symbol && totalSupply == _initialSupply
        name = _name;
        symbol = _symbol;
        decimals = _decimals;
        totalSupply = _initialSupply;
        balanceOf[msg.sender] = _initialSupply;
        emit Transfer(address(0), msg.sender, _initialSupply);
    }
    
    // Transfer function
    function transfer(address to, uint256 amount) public returns (bool) {
        //@function transfer pre: to != address(0) && balanceOf[msg.sender] >= amount
        //@function transfer post: balanceOf[msg.sender] == old(balanceOf[msg.sender]) - amount && balanceOf[to] == old(balanceOf[to]) + amount
        require(to != address(0), "Invalid recipient");
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        emit Transfer(msg.sender, to, amount);
        return true;
    }
    
    // Approve function
    function approve(address spender, uint256 amount) public returns (bool) {
        //@function approve pre: spender != address(0)
        //@function approve post: allowance[msg.sender][spender] == amount
        require(spender != address(0), "Invalid spender");
        
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
    
    // TransferFrom function
    function transferFrom(address from, address to, uint256 amount) public returns (bool) {
        //@function transferFrom pre: from != address(0) && to != address(0) && balanceOf[from] >= amount && allowance[from][msg.sender] >= amount
        //@function transferFrom post: balanceOf[from] == old(balanceOf[from]) - amount && balanceOf[to] == old(balanceOf[to]) + amount && allowance[from][msg.sender] == old(allowance[from][msg.sender]) - amount
        require(from != address(0), "Invalid sender");
        require(to != address(0), "Invalid recipient");
        require(balanceOf[from] >= amount, "Insufficient balance");
        require(allowance[from][msg.sender] >= amount, "Insufficient allowance");
        
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        allowance[from][msg.sender] -= amount;
        emit Transfer(from, to, amount);
        return true;
    }
}
"""
    
    # 4. 保存草图到临时文件
    sketch_file = "temp_erc20_sketch.txt"
    FileUtils.write_text_file(sketch_file, contract_sketch)
    
    try:
        # 5. 验证草图
        print("🔍 验证合约草图...")
        parser = SketchParser()
        validator = SketchValidator()
        
        sketch = parser.parse_file(sketch_file)
        is_valid, errors, warnings = validator.validate(sketch)
        
        if is_valid:
            print("✅ 草图验证通过")
            print(f"合约名称: {sketch.contract_name}")
            print(f"函数数量: {len(sketch.transactions)}")
        else:
            print("❌ 草图验证失败:")
            for error in errors:
                print(f"  - {error}")
            return
        
        # 6. 生成合约
        print("\n🤖 使用DeepSeek生成合约代码...")
        contract_code = await generator.generate_from_file(sketch_file)
        
        # 7. 保存生成的合约
        output_file = "generated_contracts/ERC20Token_DeepSeek.sol"
        FileUtils.write_text_file(output_file, contract_code)
        
        print(f"✅ 合约生成成功！")
        print(f"生成的代码长度: {len(contract_code)} 字符")
        print(f"输出文件: {output_file}")
        
        # 8. 显示生成的代码预览
        print("\n📄 生成的合约代码预览:")
        print("=" * 50)
        lines = contract_code.split('\n')
        for i, line in enumerate(lines[:20]):  # 显示前20行
            print(f"{i+1:2d}: {line}")
        if len(lines) > 20:
            print("...")
            print(f"完整代码已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
    
    finally:
        # 清理临时文件
        if os.path.exists(sketch_file):
            os.remove(sketch_file)


async def example_deepseek_direct_api():
    """示例：直接使用DeepSeek API"""
    print("\n=== DeepSeek直接API调用示例 ===\n")
    
    api_key = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
    
    if api_key == "your-deepseek-api-key-here":
        print("❌ 请设置DEEPSEEK_API_KEY环境变量")
        return
    
    client = DeepSeekClient(
        api_key=api_key,
        model="deepseek-chat"
    )
    
    # 直接调用API生成代码
    prompt = """
请生成一个简单的Solidity智能合约，实现一个计数器功能：
1. 有一个状态变量存储计数值
2. 有一个函数可以增加计数
3. 有一个函数可以获取当前计数值
4. 包含适当的事件和错误处理
"""
    
    try:
        print("🤖 直接调用DeepSeek API...")
        response = await client.generate(prompt, max_tokens=1000, temperature=0.1)
        
        print("✅ API调用成功！")
        print("生成的代码:")
        print("=" * 50)
        print(response.content)
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")


async def main():
    """主函数"""
    print("🚀 DeepSeek智能合约生成示例\n")
    
    # 示例1：使用生成器生成合约
    await example_deepseek_contract_generation()
    
    # 示例2：直接API调用
    await example_deepseek_direct_api()
    
    print("\n✨ 示例完成！")


if __name__ == "__main__":
    asyncio.run(main()) 