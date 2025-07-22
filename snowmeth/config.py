"""Configuration management for LLM models."""

import json
import os
from pathlib import Path
from typing import Dict

try:
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # dotenv is optional

from .exceptions import ModelError


class LLMConfig:
    """
    Manages LLM model configuration with per-step model support.

    Design: Single source of truth for default model is the DEFAULT_MODEL constant.
    All other references to the default model should use this constant or the
    get_default_model() class method.
    """

    # Single source of truth for default model
    # To change the default, only modify this line
    DEFAULT_MODEL = "openai/gpt-4o-mini"

    @classmethod
    def get_default_model(cls) -> str:
        """Get the default model without needing an instance"""
        # Allow environment variable override for development/personal use
        env_override = os.getenv("SNOWMETH_DEFAULT_MODEL")
        if env_override:
            return env_override
        return cls.DEFAULT_MODEL

    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir) / ".snowmeth"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                config = json.load(f)
                return config
        return {
            "current_story": None,
        }

    def _save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def get_model(self, step: str = "default") -> str:
        """Get model for a specific step (currently all steps use the same model)"""
        # For now, all steps use the default model
        # Future: could add per-step model configuration here
        return self.get_default_model()

    # Model configuration is now hardcoded + environment variable override
    # No need for set_model - users can set SNOWMETH_DEFAULT_MODEL env var

    def get_api_key_env(self, model: str) -> str:
        """Get required API key environment variable for a model"""
        if model.startswith("openrouter/"):
            return "OPENROUTER_API_KEY"
        elif model.startswith("openai/"):
            return "OPENAI_API_KEY"
        elif model.startswith("anthropic/"):
            return "ANTHROPIC_API_KEY"
        else:
            # Default to OpenAI for unknown prefixes
            return "OPENAI_API_KEY"

    def check_api_key(self, model: str) -> tuple[bool, str]:
        """Check if API key is available for the model"""
        api_key_env = self.get_api_key_env(model)
        api_key = os.getenv(api_key_env)

        if api_key:
            # Mask the key for display
            masked = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            return True, masked
        else:
            return False, f"Environment variable {api_key_env} not set"

    def create_lm(self, model: str):
        """Create a DSPy LM instance for the given model"""
        import dspy

        # Check API key
        has_key, key_info = self.check_api_key(model)
        if not has_key:
            api_key_env = self.get_api_key_env(model)
            raise ModelError(
                f"{api_key_env} environment variable is required for model {model}"
            )

        # Determine max_tokens based on model capabilities
        max_tokens = self._get_max_tokens_for_model(model)

        # Create LM based on model prefix
        if model.startswith("openrouter/"):
            return dspy.LM(
                model=model,
                api_base="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                temperature=0.7,  # Add temperature for variability
                max_tokens=max_tokens,
            )
        else:
            # Default DSPy behavior (works for OpenAI, Anthropic, etc.)
            return dspy.LM(model, temperature=0.7, max_tokens=max_tokens)

    def _get_max_tokens_for_model(self, model: str) -> int:
        """Get appropriate max_tokens for the model based on its context window"""
        model_lower = model.lower()
        print(
            f"DEBUG: Checking max_tokens for model: {model} (lowercase: {model_lower})"
        )

        # High context models - set reasonable output limits, not full context window
        if "flash-lite" in model_lower or "gemini-2.5-flash-lite" in model_lower:
            return 50000  # 50k output tokens (1M context window total)
        elif "gemini-2.5-pro" in model_lower:
            return 100000  # 100k output tokens (2M context window total)
        elif "claude-3.5-sonnet" in model_lower or "claude-3-opus" in model_lower:
            return 50000  # 50k output tokens (200k context window total)
        elif "gpt-4" in model_lower and (
            "turbo" in model_lower or "preview" in model_lower
        ):
            return 32000  # 32k output tokens (128k context window total)
        elif "gpt-4o-mini" in model_lower:
            return 16000  # 16k output tokens (128k context window total)
        elif "gpt-4o" in model_lower:
            return 32000  # 32k output tokens (128k context window total)
        else:
            # Conservative default for unknown models
            return 8000

    def list_models(self) -> Dict[str, str]:
        """List all configured models"""
        return self.config["models"].copy()
