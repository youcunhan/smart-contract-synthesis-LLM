#!/usr/bin/env python3
"""
环境变量使用示例

展示如何使用环境变量来设置API密钥。
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
from src.llm import DeepSeekClient, OpenAIClient, AnthropicClient


async def example_1_direct_client_creation():
    """示例1: 直接创建客户端（使用环境变量）"""
    print("=== 示例1: 直接创建客户端 ===\n")
    
    # 检查环境变量
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print("🔍 检查环境变量:")
    print(f"  DEEPSEEK_API_KEY: {'✅ 已设置' if deepseek_key else '❌ 未设置'}")
    print(f"  OPENAI_API_KEY: {'✅ 已设置' if openai_key else '❌ 未设置'}")
    print(f"  ANTHROPIC_API_KEY: {'✅ 已设置' if anthropic_key else '❌ 未设置'}")
    
    # 创建客户端（不传api_key参数，自动从环境变量获取）
    clients = []
    
    if deepseek_key:
        try:
            client = DeepSeekClient()  # 不传api_key
            clients.append(("DeepSeek", client))
            print("✅ DeepSeek客户端创建成功（使用环境变量）")
        except Exception as e:
            print(f"❌ DeepSeek客户端创建失败: {e}")
    
    if openai_key:
        try:
            client = OpenAIClient()  # 不传api_key
            clients.append(("OpenAI", client))
            print("✅ OpenAI客户端创建成功（使用环境变量）")
        except Exception as e:
            print(f"❌ OpenAI客户端创建失败: {e}")
    
    if anthropic_key:
        try:
            client = AnthropicClient()  # 不传api_key
            clients.append(("Anthropic", client))
            print("✅ Anthropic客户端创建成功（使用环境变量）")
        except Exception as e:
            print(f"❌ Anthropic客户端创建失败: {e}")
    
    return clients


async def example_2_test_api_calls(clients):
    """示例2: 测试API调用"""
    print("\n=== 示例2: 测试API调用 ===\n")
    
    for name, client in clients:
        try:
            print(f"🤖 测试 {name} API...")
            
            # 简单的测试调用
            if name == "DeepSeek":
                response = await client.generate("Hello, please respond with 'OK'", max_tokens=10)
            elif name == "OpenAI":
                response = await client.generate("Hello, please respond with 'OK'", max_tokens=10)
            elif name == "Anthropic":
                response = await client.generate("Hello, please respond with 'OK'", max_tokens=10)
            
            print(f"✅ {name} API调用成功")
            print(f"   响应: {response.content}")
            
        except Exception as e:
            print(f"❌ {name} API调用失败: {e}")


async def example_3_priority_test():
    """示例3: 测试优先级（配置文件 vs 环境变量）"""
    print("\n=== 示例3: 测试优先级 ===\n")
    
    # 模拟配置文件中的API密钥
    config_api_key = "config-file-key"
    env_api_key = os.getenv("DEEPSEEK_API_KEY")
    
    print("🔍 测试API密钥优先级:")
    print(f"  配置文件中的密钥: {config_api_key}")
    print(f"  环境变量中的密钥: {'已设置' if env_api_key else '未设置'}")
    
    # 测试1: 传入配置文件中的密钥
    try:
        client1 = DeepSeekClient(api_key=config_api_key)
        print("✅ 使用配置文件中的密钥创建客户端成功")
    except Exception as e:
        print(f"❌ 使用配置文件中的密钥创建客户端失败: {e}")
    
    # 测试2: 不传密钥，使用环境变量
    if env_api_key:
        try:
            client2 = DeepSeekClient()  # 不传api_key
            print("✅ 使用环境变量中的密钥创建客户端成功")
        except Exception as e:
            print(f"❌ 使用环境变量中的密钥创建客户端失败: {e}")


def show_environment_setup():
    """显示环境变量设置方法"""
    print("\n=== 环境变量设置方法 ===\n")
    
    print("1. 临时设置（当前会话）:")
    print("   export DEEPSEEK_API_KEY='your-api-key-here'")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print("   export ANTHROPIC_API_KEY='your-api-key-here'")
    
    print("\n2. 永久设置（添加到~/.bashrc）:")
    print("   echo 'export DEEPSEEK_API_KEY=\"your-api-key\"' >> ~/.bashrc")
    print("   echo 'export OPENAI_API_KEY=\"your-api-key\"' >> ~/.bashrc")
    print("   echo 'export ANTHROPIC_API_KEY=\"your-api-key\"' >> ~/.bashrc")
    print("   source ~/.bashrc")
    
    print("\n3. 在Python代码中设置:")
    print("   import os")
    print("   os.environ['DEEPSEEK_API_KEY'] = 'your-api-key'")
    
    print("\n4. 使用.env文件（需要python-dotenv）:")
    print("   # .env文件内容:")
    print("   DEEPSEEK_API_KEY=your-api-key")
    print("   OPENAI_API_KEY=your-api-key")
    print("   ANTHROPIC_API_KEY=your-api-key")


async def main():
    """主函数"""
    print("🚀 环境变量使用示例\n")
    
    # 示例1: 直接创建客户端
    clients = await example_1_direct_client_creation()
    
    # 示例2: 测试API调用（如果有可用的客户端）
    if clients:
        await example_2_test_api_calls(clients)
    else:
        print("\n⚠️  没有可用的API密钥，跳过API调用测试")
    
    # 示例3: 测试优先级
    await example_3_priority_test()
    
    # 显示设置方法
    show_environment_setup()
    
    print("\n✨ 示例完成！")


if __name__ == "__main__":
    asyncio.run(main()) 