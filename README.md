# Smart Contract Synthesis LLM

A large language model-based smart contract synthesis tool that can automatically generate complete smart contract code based on Solidity sketches and specifications.

## Project Overview

This project aims to realize automatic synthesis of smart contracts through LLM technology. The main features include:

1. **LLM API Management** - Unified LLM API access interface
2. **Solidity Sketch Processing** - Parse and process contract sketches containing pre-post conditions
3. **Library Documentation Management** - Natural language introduction to common Solidity libraries
4. **Code Generation** - Generate complete Solidity contracts based on input
5. **BMC Verification Preparation** - Prepare for subsequent Bounded Model Checking

## Project Structure

```
smart-contract-synthesis-LLM/
├── src/
│   ├── llm/                    # LLM API module
│   │   ├── __init__.py
│   │   ├── base.py            # Base LLM interface
│   │   ├── openai_client.py   # OpenAI client
│   │   └── anthropic_client.py # Anthropic client
│   ├── sketch/                 # Solidity sketch processing
│   │   ├── __init__.py
│   │   ├── parser.py          # Sketch parser
│   │   ├── validator.py       # Specification validator
│   │   └── examples/          # Example sketch files
│   ├── libraries/              # Library documentation management
│   │   ├── __init__.py
│   │   ├── docs_manager.py    # Documentation manager
│   │   └── docs/              # Library documentation files
│   ├── generator/              # Code generator
│   │   ├── __init__.py
│   │   ├── prompt_builder.py  # Prompt builder
│   │   ├── code_generator.py  # Code generator
│   │   └── templates/         # Generation templates
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── solidity_utils.py  # Solidity utility functions
│       └── file_utils.py      # File utility functions
├── tests/                      # Test files
├── examples/                   # Examples and demos
├── config/                     # Configuration files
├── requirements.txt            # Dependencies
└── main.py                     # Main entry point
```

## Installation and Usage

### Requirements
- Python 3.8+
- OpenAI API Key, Anthropic API Key, or DeepSeek API Key

**API密钥可以通过以下方式设置：**
1. 配置文件：在 `config/config.yaml` 中设置
2. 环境变量：设置对应的环境变量
   - `OPENAI_API_KEY` for OpenAI
   - `ANTHROPIC_API_KEY` for Anthropic  
   - `DEEPSEEK_API_KEY` for DeepSeek

### Install dependencies
```bash
pip install -r requirements.txt
```

### Basic Usage
```python
from src.generator.code_generator import ContractGenerator
from src.sketch.parser import SketchParser

# Parse Solidity sketch
parser = SketchParser()
sketch = parser.parse_file("examples/sheep_farm_sketch.txt")

# Generate contract
generator = ContractGenerator()
contract = generator.generate(sketch)

# Save generated contract
with open("generated_contract.sol", "w") as f:
    f.write(contract)
```

## Configuration

Configure your API key and other settings in `config/config.yaml`:

```yaml
llm:
  provider: "deepseek"  # "openai", "anthropic", or "deepseek"
  api_key: "your-deepseek-api-key"  # 或使用环境变量 DEEPSEEK_API_KEY
  model: "deepseek-chat"
  
  # DeepSeek特定配置
  deepseek:
    base_url: "https://api.deepseek.com"
    timeout: 60

generation:
  max_tokens: 4000
  temperature: 0.1
```

**或者使用环境变量（推荐）：**
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
# 然后配置文件中的 api_key 可以设为空或占位符
```
