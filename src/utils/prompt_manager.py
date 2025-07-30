import os
from typing import List, Optional

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'prompts')

class PromptManager:
    """
    Utility class for managing prompt templates stored in the prompts directory.
    Supports loading, listing, and retrieving prompt templates by name or path.
    """
    def __init__(self, prompt_dir: Optional[str] = None):
        self.prompt_dir = prompt_dir or PROMPT_DIR

    def list_prompts(self) -> List[str]:
        """
        List all prompt template files in the prompt directory.
        Returns a list of filenames.
        """
        return [f for f in os.listdir(self.prompt_dir) if os.path.isfile(os.path.join(self.prompt_dir, f))]

    def load_prompt(self, name: str) -> str:
        """
        Load the content of a prompt template by filename.
        Returns the content as a string.
        """
        path = os.path.join(self.prompt_dir, name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt template '{name}' not found in {self.prompt_dir}")
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_prompt_path(self, name: str) -> str:
        """
        Get the absolute path of a prompt template by filename.
        """
        return os.path.abspath(os.path.join(self.prompt_dir, name)) 