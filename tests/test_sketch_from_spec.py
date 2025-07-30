import asyncio
import os
from src.generator.sketch_from_spec import SketchFromSpecGenerator
from src.llm.openai_client import OpenAIClient  # or use your default LLM client

class DummyLLMClient:
    async def generate_with_system_prompt(self, system_prompt, user_prompt, max_tokens, temperature):
        # Return a dummy sketch for testing
        class Response:
            content = (
                "contract TestToken {\n"
                "    uint256 public totalSupply;\n"
                "    struct Holder { address addr; uint256 balance; }\n"
                "    event Transfer(address from, address to, uint256 amount);\n"
                "    function transfer(address to, uint256 amount) external { ... }\n"
                "}"
            )
        return Response()

async def test_generate_sketch_from_spec():
    llm_client = DummyLLMClient()
    generator = SketchFromSpecGenerator(llm_client)
    spec = "A simple ERC20-like token with transfer functionality."
    sketch = await generator.generate_sketch(spec)
    assert "contract" in sketch
    assert "function transfer" in sketch
    assert "event Transfer" in sketch
    print("Test passed: sketch generated from spec.")

if __name__ == "__main__":
    asyncio.run(test_generate_sketch_from_spec()) 