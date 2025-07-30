"""
提示词构建器

构建用于LLM的输入提示，包含sketch、规范和库信息。
"""

import os
from src.utils.prompt_manager import PromptManager
from src.sketch.models import Sketch

PROMPT_TEMPLATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'prompts', 'smart_contract_generation.txt')

class PromptBuilder:
    def __init__(self, library_manager):
        self.library_manager = library_manager
        self.prompt_manager = PromptManager()

    def build_generation_prompt(self, sketch, library_names=None):
        """
        Build the code generation prompt using the template in prompts/smart_contract_generation.txt.
        Fills in {sketch} and {library_docs} placeholders dynamically.
        If library_names is provided, only those libraries' docs are injected.
        """
        template = self.prompt_manager.load_prompt('smart_contract_generation.txt')
        sketch_str = self._sketch_to_string(sketch)
        library_docs = self._build_library_docs_section(sketch, library_names)
        prompt = template.replace('{sketch}', sketch_str).replace('{library_docs}', library_docs)
        return prompt

    def _sketch_to_string(self, sketch):
        # You can adapt the existing _sketch_to_string logic here, but output in English
        section = f"Contract Name: {sketch.contract_name}\n\n"
        if sketch.imports:
            section += "### Imports\n"
            for imp in sketch.imports:
                section += f"```solidity\n{imp}\n```\n"
            section += "\n"
        if sketch.state_variables:
            section += "### State Variables\n"
            for var in sketch.state_variables:
                section += f"```solidity\n{var}\n```\n"
            section += "\n"
        if sketch.structs:
            section += "### Struct Definitions\n"
            for struct in sketch.structs:
                section += f"```solidity\n{struct}\n```\n"
            section += "\n"
        if sketch.events:
            section += "### Event Definitions\n"
            for event in sketch.events:
                section += f"```solidity\n{event}\n```\n"
            section += "\n"
        if sketch.transactions:
            section += "### Function Definitions\n"
            for tx in sketch.transactions:
                section += f"#### {tx.name}\n"
                section += f"```solidity\nfunction {tx.name}("
                if tx.parameters:
                    section += ", ".join(tx.parameters)
                section += f") {tx.visibility}"
                if tx.return_type:
                    section += f" returns ({tx.return_type})"
                section += "\n```\n"
                if tx.sketch_code:
                    section += f"Sketch code:\n```solidity\n{tx.sketch_code}\n```\n"
                section += "\n"
        return section

    def _build_library_docs_section(self, sketch, library_names=None):
        if library_names:
            return self.library_manager.generate_library_prompt_for_names(library_names)
        else:
            return self.library_manager.generate_library_prompt(self._sketch_to_string(sketch))

    def build_validation_prompt(self, generated_code: str, sketch: Sketch) -> str:
        """构建验证提示词"""
        prompt = """You are a Solidity code validation expert. Please verify that the generated contract code meets the original sketch requirements.

## Validation Task

Please check if the generated code:

1. **Function Completeness**: Implements all functions defined in the sketch
2. **Specification Conformity**: Meets all pre-conditions and post-conditions
3. **Security**: No obvious security vulnerabilities
4. **Correctness**: Code syntax is correct, logic is reasonable

## Generated Code

```solidity
{generated_code}
```

## Original Sketch

{sketch_summary}

## Validation Result

Please provide a detailed validation report, including:
- Function Completeness Check
- Specification Conformity Check
- Security Check
- Found issues and suggestions
- Overall Evaluation

"""
        
        sketch_summary = self._build_sketch_summary(sketch)
        return prompt.format(generated_code=generated_code, sketch_summary=sketch_summary)
    
    def _build_sketch_summary(self, sketch: Sketch) -> str:
        """构建草图摘要"""
        summary = f"Contract Name: {sketch.contract_name}\n\n"
        
        summary += "Function List:\n"
        for tx in sketch.transactions:
            summary += f"- {tx.name}("
            if tx.parameters:
                summary += ", ".join(tx.parameters)
            summary += f") {tx.visibility}\n"
        
        summary += "\nSpecification Requirements:\n"
        for tx in sketch.transactions:
            if tx.spec:
                summary += f"- {tx.name}: pre={tx.spec.pre_condition}, post={tx.spec.post_condition}\n"
        
        return summary 