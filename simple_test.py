#!/usr/bin/env python3
"""
简化的DeepSeek测试脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_basic_imports():
    """测试基本导入"""
    print("🔍 测试基本模块导入...")
    
    try:
        from src.llm import DeepSeekClient
        print("✅ DeepSeekClient导入成功")
    except Exception as e:
        print(f"❌ DeepSeekClient导入失败: {e}")
        return False
    
    try:
        from src.utils import FileUtils
        print("✅ FileUtils导入成功")
    except Exception as e:
        print(f"❌ FileUtils导入失败: {e}")
        return False
    
    return True

async def test_config_reading():
    """测试配置文件读取"""
    print("\n🔍 测试配置文件读取...")
    
    try:
        from src.utils import FileUtils
        
        config_file = Path("config/config.yaml")
        if not config_file.exists():
            print("❌ 配置文件不存在")
            return False
        
        config = FileUtils.read_yaml_file("config/config.yaml")
        print("✅ 配置文件读取成功")
        
        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "")
        api_key = llm_config.get("api_key", "")
        
        print(f"提供商: {provider}")
        print(f"API密钥: {'已设置' if api_key and api_key != 'your-deepseek-api-key-here' else '未设置'}")
        
        return provider == "deepseek" and api_key and api_key != "your-deepseek-api-key-here"
        
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return False

async def test_deepseek_client():
    """测试DeepSeek客户端"""
    print("\n🔍 测试DeepSeek客户端...")
    
    try:
        from src.llm import DeepSeekClient
        from src.utils import FileUtils
        
        config = FileUtils.read_yaml_file("config/config.yaml")
        llm_config = config["llm"]
        api_key = llm_config["api_key"]
        
        # 检查是否使用环境变量
        if api_key == "your-deepseek-api-key-here":
            env_api_key = os.getenv("DEEPSEEK_API_KEY")
            if env_api_key:
                print("✅ 将使用环境变量中的API密钥")
                api_key = None  # 让客户端从环境变量获取
            else:
                print("❌ 请先设置正确的API密钥（配置文件或环境变量）")
                return False
        
        client = DeepSeekClient(
            api_key=api_key,  # 如果为None，客户端会自动从环境变量获取
            model=llm_config["model"]
        )
        print("✅ DeepSeek客户端创建成功")
        
        # 测试简单调用
        print("正在测试API调用...")
        response = await client.generate("Hello", max_tokens=10)
        
        if response.content:
            print("✅ API调用成功")
            print(f"响应: {response.content}")
            return True
        else:
            print("❌ API调用失败")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek客户端测试失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 DeepSeek配置测试\n")
    
    # 测试1: 基本导入
    if not await test_basic_imports():
        print("\n❌ 基本导入测试失败，请检查项目结构")
        return
    
    # 测试2: 配置文件
    if not await test_config_reading():
        print("\n❌ 配置文件测试失败，请检查配置")
        return
    
    # 测试3: DeepSeek客户端
    if not await test_deepseek_client():
        print("\n❌ DeepSeek客户端测试失败")
        return
    
    print("\n🎉 所有测试通过！DeepSeek配置正确。")

if __name__ == "__main__":
    asyncio.run(main()) 