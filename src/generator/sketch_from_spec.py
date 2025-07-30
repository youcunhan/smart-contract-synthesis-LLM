import os
from typing import Optional

class SketchFromSpecGenerator:
    """
    Uses an LLM to generate a contract sketch from a natural language specification.
    """
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def generate_sketch(self, spec: str) -> str:
        """
        Generate a sketch from a natural language specification using the LLM.
        Returns the sketch as a string.
        """
        prompt = self._build_prompt(spec)
        response = await self.llm_client.generate_with_system_prompt(
            system_prompt="You are a Solidity smart contract architect. Your job is to design a contract sketch based on the following requirements.",
            user_prompt=prompt,
            max_tokens=1500,
            temperature=0.2
        )
        return response.content.strip()

    def _build_prompt(self, spec: str) -> str:
        # Load prompt template from prompts/sketch_from_spec.txt
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'prompts', 'sketch_from_spec.txt')
        prompt_path = os.path.abspath(prompt_path)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = f.read()
        return template.replace('{spec}', spec) 