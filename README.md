# Smart Contract Synthesis LLM

A large language model-based smart contract synthesis tool that can automatically generate complete smart contract code from Solidity sketches and specifications.

## 🚀 Project Overview

This project aims to realize automatic synthesis of smart contracts through LLM technology. The main features include:

1. **LLM API Management** - Unified LLM API access interface (supports OpenAI, Anthropic, DeepSeek)
2. **Solidity Sketch Processing** - Parse and process contract sketches containing pre/post conditions
3. **Specification to Sketch Generation** - Automatically generate contract sketches from formal specifications
4. **Library Documentation Management** - Natural language introduction to common Solidity libraries
5. **Code Generation** - Generate complete Solidity contracts based on input
6. **Validation Functionality** - Validate sketch validity and consistency(bmc in progress)

## 📁 Project Structure

```
smart-contract-synthesis-LLM/
├── src/
│   ├── llm/                    # LLM API module
│   │   ├── base.py            # LLM base interface
│   │   ├── openai_client.py   # OpenAI client
│   │   ├── deepseek_client.py # DeepSeek client
│   │   └── anthropic_client.py # Anthropic client
│   ├── sketch/                 # Solidity sketch processing
│   │   ├── parser.py          # Sketch parser
│   │   ├── validator.py       # Specification validator(bmc in progress)
│   │   └── models.py          # Data models
│   ├── generator/              # Code generator
│   │   ├── code_generator.py  # Contract code generator
│   │   ├── sketch_from_spec.py # Generate sketch from specification
│   │   └── prompt_builder.py  # Prompt builder
│   ├── libraries/              # Library documentation management
│   │   ├── docs_manager.py    # Documentation manager
│   │   └── docs/              # Library documentation files
│   └── utils/                  # Utility functions
│       └── file_utils.py      # File utility functions
├── sketchs/                    # Sketch example files
│   ├── simple_erc20_sketch.txt
│   └── ...
├── specs/                      # Specification files
│   ├── simple_erc20.spec.txt
│   └── ...
├── prompts/                    # Prompt templates
│   ├── sketch_from_spec.txt
│   └── ...
├── examples/                   # Usage examples
├── config/                     # Configuration files
├── generated_contracts/        # Generated contracts
├── tests/                      # Test files
├── logs/                       # Log files
├── main.py                     # Main program entry
└── requirements.txt            # Dependencies
```

## 🛠️ Installation and Configuration

### System Requirements
- Python 3.8+
- OpenAI API Key, Anthropic API Key, or DeepSeek API Key

### Install Dependencies
```bash
pip install -r requirements.txt
```

### API Key Configuration

**Method 1: Configuration File (Recommended)**
Set in `config/config.yaml`:
```yaml
llm:
  provider: "deepseek"  # "openai", "anthropic", or "deepseek"
  api_key: "your-api-key-here"
  model: "deepseek-chat"
  
  # DeepSeek specific configuration
  deepseek:
    base_url: "https://api.deepseek.com"
    timeout: 60

generation:
  max_tokens: 4000
  temperature: 0.1
```

**Method 2: Environment Variables**
```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 📖 Usage

### Command Line Tool

The project provides a complete command line tool supporting various operations:

#### 1. View Available Examples
```bash
# View available sketch files
python main.py examples

# View available specification files
python main.py specs
```

#### 2. Validate Sketch Files
```bash
python main.py validate --sketch sketchs/simple_erc20_sketch.txt
```

#### 3. Generate Sketch from Specification
```bash
python main.py sketch-from-spec --spec specs/simple_erc20.spec.txt --output generated_sketch.txt
```

#### 4. Generate Contract from Sketch
```bash
python main.py generate --sketch sketchs/sheep_farm_sketch.txt --output generated_contract.sol
```

#### 5. View Available Libraries
```bash
# List all available libraries
python main.py libraries

# View detailed information about a specific library
python main.py library-info --library openzeppelin
```

#### 6. Generate Contract with Specific Library
```bash
python main.py generate --sketch sketchs/simple_erc20_sketch.txt --library openzeppelin --output contract_with_lib.sol
```

### Programming Interface

#### Basic Usage Example
```python
from src.sketch import SketchParser, SketchValidator
from src.generator import ContractGenerator
from src.llm import OpenAIClient

# 1. Parse sketch
parser = SketchParser()
sketch = parser.parse_file("sketchs/sheep_farm_sketch.txt")

# 2. Validate sketch
validator = SketchValidator()
is_valid, errors, warnings = validator.validate(sketch)

# 3. Generate contract
llm_client = OpenAIClient(api_key="your-api-key")
generator = ContractGenerator(llm_client)
contract_code = await generator.generate_from_sketch(sketch)

# 4. Save contract
with open("generated_contract.sol", "w") as f:
    f.write(contract_code)
```

#### Generate Sketch from Specification
```python
from src.generator.sketch_from_spec import SketchFromSpecGenerator
from src.llm import DeepSeekClient

# Read specification file
with open("specs/simple_erc20.spec.txt", "r") as f:
    spec_content = f.read()

# Generate sketch
llm_client = DeepSeekClient(api_key="your-api-key")
generator = SketchFromSpecGenerator(llm_client)
sketch_text = await generator.generate_sketch(spec_content)
```

## 📋 File Format Specifications

### Sketch File Format
Sketch files use special comment format to define pre/post conditions:

```solidity
contract Token {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    
    //@global invariant: totalSupply >= 0
    
    function mint(uint256 amount) external {
        //@function mint pre: amount > 0
        //@function mint post: totalSupply == old(totalSupply) + amount
        // Implementation code...
    }
    
    function transfer(address to, uint256 amount) external returns (bool) {
        //@function transfer pre: balances[msg.sender] >= amount
        //@function transfer post: balances[msg.sender] == old(balances[msg.sender]) - amount
        // Implementation code...
    }
}
```

### Specification File Format
Specification files use concise text format:

```
Global: totalSupply >= 0.
Local: function mint(uint256 amount): pre: amount > 0, post: totalSupply == old(totalSupply) + amount.
Local: function transfer(address to, uint256 amount): pre: balances[msg.sender] >= amount, post: balances[msg.sender] == old(balances[msg.sender]) - amount, balances[to] == old(balances[to]) + amount.
```

## 🔧 Advanced Features

### Prompt Debugging
All LLM calls automatically save prompts to `prompt.tmp` file for debugging and optimization.

### Multi-LLM Provider Support
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **DeepSeek**: deepseek-chat
- **Anthropic**: Claude-3

### Library Integration
Supports integration with common Solidity libraries:
- OpenZeppelin
- Solmate
- Dappsys
- Custom libraries

## 📝 Example Files

The project includes multiple example files:

### Sketch Examples
- `sketchs/simple_erc20_sketch.txt` - Simple ERC20 token
- `sketchs/sheep_farm_sketch.txt` - Sheep farm game contract
- ... (more sketch files)

### Specification Examples
- `specs/simple_erc20.spec.txt` - ERC20 token specification
- `specs/auction.spec.txt` - Auction contract specification
- `specs/ownership.spec.txt` - Ownership management specification
- ... (more specification files)

### Usage Examples
- `examples/usage_example.py` - Basic usage example
- `examples/deepseek_example.py` - DeepSeek API example
- `examples/env_var_example.py` - Environment variable configuration example

## 🧪 Testing

Run tests:
```bash
python -m pytest tests/
```

## 📊 Logging

Log files are saved in the `logs/` directory, containing detailed execution information.

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve the project.

## 📄 License

This project is licensed under the MIT License.
