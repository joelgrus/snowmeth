"""Configuration management for LLM models."""

import json
import os
from pathlib import Path
from typing import Dict

import click


class LLMConfig:
    """Manages LLM model configuration with per-step model support"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir) / ".snowmeth"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Migrate old config format
                if "models" not in config:
                    config["models"] = {"default": "openai/gpt-4o-mini"}
                return config
        return {
            "current_story": None,
            "models": {
                "default": "openai/gpt-4o-mini",
                # Future: per-step models
                # "sentence_generation": "openai/gpt-4o-mini",
                # "paragraph_expansion": "openrouter/google/gemini-2.5-flash-lite-preview-06-17",
                # "character_extraction": "openai/gpt-4o",
                # "plot_expansion": "openrouter/google/gemini-2.5-pro-preview",
                # "content_refinement": "openai/gpt-4o-mini"
            }
        }
    
    def _save_config(self):
        """Save configuration to file"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_model(self, step: str = "default") -> str:
        """Get model for a specific step"""
        return self.config["models"].get(step, self.config["models"]["default"])
    
    def set_model(self, model: str, step: str = "default"):
        """Set model for a specific step"""
        self.config["models"][step] = model
        self._save_config()
    
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
            raise click.ClickException(f"{api_key_env} environment variable is required for model {model}")
        
        # Create LM based on model prefix
        if model.startswith("openrouter/"):
            return dspy.LM(
                model=model,
                api_base="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY"),
            )
        else:
            # Default DSPy behavior (works for OpenAI, Anthropic, etc.)
            return dspy.LM(model)
    
    def list_models(self) -> Dict[str, str]:
        """List all configured models"""
        return self.config["models"].copy()