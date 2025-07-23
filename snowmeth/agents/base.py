"""Base agent class and common utilities for the Snowflake Method agents."""

import dspy
import logging
from ..config import LLMConfig
from ..exceptions import ModelError

logger = logging.getLogger(__name__)


def clean_json_markdown(content: str) -> str:
    """Clean up potential markdown formatting from JSON content."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.endswith("```"):
        content = content[:-3]  # Remove ```
    return content.strip()


class BaseAgent:
    """Base class for all Snowflake Method step agents."""
    
    def __init__(self, model_name: str = "default"):
        """Initialize the agent with LLM configuration.
        
        Args:
            model_name: Name of the model configuration to use
        """
        self.llm_config = LLMConfig()
        self.model_name = model_name
        
        try:
            model = self.llm_config.get_model(model_name)
            self.lm = self.llm_config.create_lm(model)
            dspy.configure(lm=self.lm)
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise ModelError(f"Failed to initialize model '{model_name}': {str(e)}")
    
    def generate(self, **kwargs) -> str:
        """Generate content for this step. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement generate()")
    
    def refine(self, content: str, instructions: str, **kwargs) -> str:
        """Refine existing content. To be implemented by subclasses if needed."""
        raise NotImplementedError("Subclasses must implement refine() if refinement is supported")