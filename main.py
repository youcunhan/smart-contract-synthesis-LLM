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

from src.llm import OpenAIClient, AnthropicClient
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
        
        if not api_key:
            raise ValueError("Please set your API key in config/config.yaml")
        
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
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    async def generate_contract(self, sketch_file: str, output_file: Optional[str] = None) -> str:
        """Generate contract"""
        print(f"Parsing sketch file: {sketch_file}")
        
        # Parse sketch
        sketch = self.parser.parse_file(sketch_file)
        
        # Validate sketch
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
        
        # Generate contract
        print("🤖 Generating contract code with LLM...")
        contract_code = await self.generator.generate_from_sketch(sketch)
        
        # Save contract
        if output_file:
            FileUtils.write_text_file(output_file, contract_code)
            print(f"✅ Contract saved to: {output_file}")
        else:
            # Use default output path
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
        examples_dir = Path("src/sketch/examples")
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


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Smart Contract Synthesis LLM")
    parser.add_argument("command", choices=["generate", "validate", "libraries", "library-info", "examples"], 
                       help="Command to execute")
    parser.add_argument("--sketch", "-s", help="Path to sketch file")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--library", "-l", help="Library name (for library-info command)")
    parser.add_argument("--config", "-c", default="config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    try:
        synthesizer = SmartContractSynthesizer(args.config)
        
        if args.command == "generate":
            if not args.sketch:
                print("❌ Please specify the sketch file path (--sketch)")
                return
            await synthesizer.generate_contract(args.sketch, args.output)
        
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
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 