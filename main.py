#!/usr/bin/env python3
"""
Smart Contract Synthesis LLM Main Program

Use LLM to generate complete Solidity contract code based on sketch and specification.
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.llm import OpenAIClient, AnthropicClient, DeepSeekClient
from src.generator import ContractGenerator
from src.sketch import SketchParser, SketchValidator
from src.libraries import LibraryDocsManager
from src.utils import FileUtils


class SmartContractSynthesizer:
    """Main class for smart contract synthesis"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = FileUtils.read_yaml_file(config_path)
        self.llm_client = self._create_llm_client()
        self.generator = ContractGenerator(self.llm_client)
        self.parser = SketchParser()
        self.validator = SketchValidator()
        self.library_manager = LibraryDocsManager()
    
    def _create_llm_client(self):
        """Create LLM client"""
        llm_config = self.config["llm"]
        provider = llm_config["provider"]
        api_key = llm_config["api_key"]
        
        # 如果配置文件中没有API密钥，尝试从环境变量获取
        if not api_key or api_key == "your-deepseek-api-key-here":
            if provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
            elif provider == "deepseek":
                api_key = os.getenv("DEEPSEEK_API_KEY")
            
            if api_key:
                print(f"✅ 从环境变量获取{provider} API密钥")
            else:
                raise ValueError(f"Please set your {provider.upper()}_API_KEY environment variable or in config/config.yaml")
        
        if provider == "openai":
            return OpenAIClient(
                api_key=api_key,
                model=llm_config["model"],
                max_tokens=llm_config["max_tokens"],
                temperature=llm_config["temperature"]
            )
        elif provider == "anthropic":
            return AnthropicClient(
                api_key=api_key,
                model=llm_config["model"],
                max_tokens=llm_config["max_tokens"],
                temperature=llm_config["temperature"]
            )
        elif provider == "deepseek":
            # 获取DeepSeek特定配置
            deepseek_config = llm_config.get("deepseek", {})
            return DeepSeekClient(
                api_key=api_key,
                model=llm_config["model"],
                max_tokens=llm_config["max_tokens"],
                temperature=llm_config["temperature"],
                base_url=deepseek_config.get("base_url", "https://api.deepseek.com"),
                timeout=deepseek_config.get("timeout", 60)
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def generate_contract(self, sketch_file: str, output_file: Optional[str] = None, library_names: Optional[list] = None) -> str:
        """Generate contract, optionally with specific libraries."""
        print(f"Parsing sketch file: {sketch_file}")
        sketch = self.parser.parse_file(sketch_file)
        is_valid, errors, warnings = self.validator.validate(sketch)
        if not is_valid:
            print("❌ Sketch validation failed:")
            for error in errors:
                print(f"  - {error}")
            raise ValueError("Sketch validation failed")
        if warnings:
            print("⚠️  Warning:")
            for warning in warnings:
                print(f"  - {warning}")
        print(f"✅ Sketch validation passed, contract name: {sketch.contract_name}")
        print("🤖 Generating contract code with LLM...")
        contract_code = await self.generator.generate_from_sketch(sketch, library_names=library_names)
        if output_file:
            FileUtils.write_text_file(output_file, contract_code)
            print(f"✅ Contract saved to: {output_file}")
        else:
            default_output = f"generated_contracts/{sketch.contract_name}.sol"
            FileUtils.write_text_file(default_output, contract_code)
            print(f"✅ Contract saved to: {default_output}")
        return contract_code
    
    async def validate_sketch(self, sketch_file: str):
        """Validate sketch file"""
        print(f"Validating sketch file: {sketch_file}")
        
        sketch = self.parser.parse_file(sketch_file)
        is_valid, errors, warnings = self.validator.validate(sketch)
        
        if is_valid:
            print("✅ Sketch validation passed")
            print(f"Contract name: {sketch.contract_name}")
            print(f"Number of functions: {len(sketch.transactions)}")
            print(f"Number of state variables: {len(sketch.state_variables)}")
        else:
            print("❌ Sketch validation failed:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("⚠️  Warning:")
            for warning in warnings:
                print(f"  - {warning}")
    
    def list_libraries(self):
        """List available libraries"""
        libraries = self.library_manager.get_all_libraries()
        print("📚 Available Solidity libraries:")
        for lib_name in libraries:
            library = self.library_manager.get_library(lib_name)
            if library:
                print(f"  - {library.name}: {library.description}")
    
    def show_library_info(self, library_name: str):
        """Show library details"""
        library = self.library_manager.get_library(library_name)
        if library:
            print(f"📚 {library.name}")
            print(f"Description: {library.description}")
            print("\nMain features:")
            for func in library.functions:
                print(f"  - {func['name']}: {func['description']}")
            print("\nBest practices:")
            for practice in library.best_practices:
                print(f"  - {practice}")
        else:
            print(f"❌ Library '{library_name}' not found")
    
    def list_examples(self):
        """List example sketch files"""
        examples_dir = Path("sketchs")
        if examples_dir.exists():
            sketch_files = list(examples_dir.glob("*.txt"))
            if sketch_files:
                print("📝 Example sketch files:")
                for file in sketch_files:
                    print(f"  - {file.name}")
            else:
                print("📝 No example sketch files found")
        else:
            print("📝 Example directory does not exist")
    
    def list_specs(self):
        """List available specification files"""
        specs_dir = Path("specs")
        if specs_dir.exists():
            spec_files = list(specs_dir.glob("*.spec.txt"))
            if spec_files:
                print("📋 Available specification files:")
                for file in spec_files:
                    print(f"  - {file.name}")
            else:
                print("📋 No specification files found")
        else:
            print("📋 Specs directory does not exist")

    async def generate_sketch_from_spec(self, spec_file: str, output_file: str) -> str:
        """Generate a sketch from a specification file using LLM and save it."""
        print(f"🤖 Generating sketch from spec file: {spec_file}")
        
        # 读取spec文件
        spec_path = Path(spec_file)
        if not spec_path.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_file}")
        
        spec_content = spec_path.read_text(encoding='utf-8')
        print(f"📖 Read specification from: {spec_file}")
        
        from src.generator.sketch_from_spec import SketchFromSpecGenerator
        sketch_generator = SketchFromSpecGenerator(self.llm_client)
        sketch_text = await sketch_generator.generate_sketch(spec_content)
        FileUtils.write_text_file(output_file, sketch_text)
        print(f"✅ Sketch saved to: {output_file}")
        return sketch_text


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Smart Contract Synthesis LLM")
    parser.add_argument("command", choices=["generate", "validate", "libraries", "library-info", "examples", "specs", "sketch-from-spec"], 
                       help="Command to execute")
    parser.add_argument("--sketch", "-s", help="Path to sketch file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--library", "-l", help="Comma-separated library names (for generate/library-info command)")
    parser.add_argument("--config", "-c", default="config/config.yaml", help="Path to config file")
    parser.add_argument("--spec", help="Path to specification file for sketch-from-spec command")
    
    args = parser.parse_args()
    
    try:
        synthesizer = SmartContractSynthesizer(args.config)
        
        if args.command == "generate":
            if not args.sketch:
                print("❌ Please specify the sketch file path (--sketch)")
                return
            library_names = None
            if args.library:
                library_names = [name.strip() for name in args.library.split(",") if name.strip()]
            await synthesizer.generate_contract(args.sketch, args.output, library_names=library_names)
        
        elif args.command == "validate":
            if not args.sketch:
                print("❌ Please specify the sketch file path (--sketch)")
                return
            await synthesizer.validate_sketch(args.sketch)
        
        elif args.command == "libraries":
            synthesizer.list_libraries()
        
        elif args.command == "library-info":
            if not args.library:
                print("❌ Please specify the library name (--library)")
                return
            synthesizer.show_library_info(args.library)
        
        elif args.command == "examples":
            synthesizer.list_examples()
        
        elif args.command == "specs":
            synthesizer.list_specs()
        
        elif args.command == "sketch-from-spec":
            if not args.spec or not args.output:
                print("❌ Please specify both --spec (specification file path) and --output for sketch-from-spec command")
                return
            await synthesizer.generate_sketch_from_spec(args.spec, args.output)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 