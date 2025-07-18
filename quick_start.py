#!/usr/bin/env python3
"""
Smart Contract Synthesis LLM Quick Start Script

Help users quickly get started with this project.
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check project requirements"""
    print("🔍 Checking project requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Check required files
    required_files = [
        "requirements.txt",
        "config/config.yaml",
        "src/llm/__init__.py",
        "src/sketch/__init__.py",
        "src/generator/__init__.py",
        "src/libraries/__init__.py",
        "src/utils/__init__.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
    
    print("✅ All required files exist")
    return True


def install_dependencies():
    """Install dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_config():
    """Setup configuration"""
    print("\n⚙️  Setting up configuration...")
    
    config_file = "config/config.yaml"
    if not Path(config_file).exists():
        print(f"❌ Config file does not exist: {config_file}")
        return False
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY environment variable is not set")
        print("Please set the environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("Or set it directly in config/config.yaml")
        return False
    
    print("✅ API key is set")
    return True


def create_directories():
    """Create required directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "generated_contracts",
        "logs",
        "src/libraries/docs",
        "src/generator/templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def run_basic_test():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from src.sketch import SketchParser
        from src.libraries import LibraryDocsManager
        from src.utils import FileUtils
        
        print("✅ Module import successful")
        
        # Test sketch parser
        parser = SketchParser()
        print("✅ Sketch parser created successfully")
        
        # Test library manager
        library_manager = LibraryDocsManager()
        libraries = library_manager.get_all_libraries()
        print(f"✅ Library manager works, found {len(libraries)} libraries")
        
        # Test file utils
        test_content = "test content"
        test_file = "test_file.txt"
        FileUtils.write_text_file(test_file, test_content)
        read_content = FileUtils.read_text_file(test_file)
        
        if read_content == test_content:
            print("✅ File utils work correctly")
        else:
            print("❌ File utils test failed")
        
        # Clean up test file
        Path(test_file).unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def show_next_steps():
    """Show next steps"""
    print("\n🎯 Next steps:")
    print("1. Set your API key:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    print()
    print("2. Validate a sketch file:")
    print("   python main.py validate --sketch src/sketch/examples/sheep_farm_sketch.txt")
    print()
    print("3. Generate a contract:")
    print("   python main.py generate --sketch src/sketch/examples/sheep_farm_sketch.txt")
    print()
    print("4. List available libraries:")
    print("   python main.py libraries")
    print()
    print("5. Run the full example:")
    print("   python examples/usage_example.py")
    print()
    print("📚 For more information, see README.md")


def main():
    """Main function"""
    print("🚀 Smart Contract Synthesis LLM Quick Start")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Project requirements check failed, please fix the above issues")
        return
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        return
    
    # Setup config
    if not setup_config():
        print("\n⚠️  Configuration is incomplete, but you can continue")
    
    # Create directories
    create_directories()
    
    # Run tests
    if not run_basic_test():
        print("\n❌ Basic test failed")
        return
    
    print("\n✅ Quick start complete!")
    show_next_steps()


if __name__ == "__main__":
    main() 