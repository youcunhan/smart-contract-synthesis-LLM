#!/usr/bin/env python3
"""
DeepSeek配置测试脚本

测试DeepSeek客户端是否正常工作。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.llm import DeepSeekClient
from src.utils import FileUtils


async def test_deepseek_connection():
    """测试DeepSeek连接"""
    print("🔍 测试DeepSeek连接...")
    
    # 读取配置
    try:
        config = FileUtils.read_yaml_file("config/config.yaml")
        llm_config = config["llm"]
        api_key = llm_config["api_key"]
        
        if api_key == "your-deepseek-api-key-here":
            print("❌ 请在config/config.yaml中设置你的DeepSeek API密钥")
            return False
        
        # 创建DeepSeek客户端
        deepseek_config = llm_config.get("deepseek", {})
        client = DeepSeekClient(
            api_key=api_key,
            model=llm_config["model"],
            base_url=deepseek_config.get("base_url", "https://api.deepseek.com"),
            timeout=deepseek_config.get("timeout", 60)
        )
        
        # 测试简单生成
        print("🤖 测试简单文本生成...")
        response = await client.generate("Hello, please respond with 'DeepSeek is working!'", max_tokens=50)
        print(f"✅ 响应: {response.content}")
        
        # 测试系统提示词
        print("\n🤖 测试系统提示词...")
        response = await client.generate_with_system_prompt(
            system_prompt="你是一个专业的Solidity智能合约开发专家。",
            user_prompt="请简要介绍Solidity智能合约的基本结构。",
            max_tokens=200
        )
        print(f"✅ 响应: {response.content[:100]}...")
        
        print("\n🎉 DeepSeek配置测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


async def test_contract_generation():
    """测试合约生成"""
    print("\n🔍 测试合约生成...")
    
    try:
        from src.generator import ContractGenerator
        from src.llm import DeepSeekClient
        from src.utils import FileUtils
        
        # 读取配置
        config = FileUtils.read_yaml_file("config/config.yaml")
        llm_config = config["llm"]
        api_key = llm_config["api_key"]
        
        # 创建客户端和生成器
        deepseek_config = llm_config.get("deepseek", {})
        client = DeepSeekClient(
            api_key=api_key,
            model=llm_config["model"],
            base_url=deepseek_config.get("base_url", "https://api.deepseek.com"),
            timeout=deepseek_config.get("timeout", 60)
        )
        
        generator = ContractGenerator(client)
        
        # 创建一个简单的sketch
        simple_sketch = """
contract SimpleStorage {
    uint256 public value;
    
    function setValue(uint256 newValue) public {
        //@function setValue pre: newValue >= 0
        //@function setValue post: value == newValue
        value = newValue;
    }
    
    function getValue() public view returns (uint256) {
        return value;
    }
}
"""
        
        # 保存sketch到临时文件
        temp_sketch_file = "temp_test_sketch.txt"
        FileUtils.write_text_file(temp_sketch_file, simple_sketch)
        
        # 生成合约
        contract_code = await generator.generate_from_file(temp_sketch_file)
        
        print(f"✅ 合约生成成功！")
        print(f"生成的代码长度: {len(contract_code)} 字符")
        print(f"代码预览:\n{contract_code[:200]}...")
        
        # 清理临时文件
        os.remove(temp_sketch_file)
        
        return True
        
    except Exception as e:
        print(f"❌ 合约生成测试失败: {e}")
        return False


async def main():
    """主函数"""
    print("🚀 DeepSeek配置测试开始...\n")
    
    # 测试连接
    connection_ok = await test_deepseek_connection()
    
    if connection_ok:
        # 测试合约生成
        await test_contract_generation()
    
    print("\n✨ 测试完成！")


if __name__ == "__main__":
    asyncio.run(main()) 