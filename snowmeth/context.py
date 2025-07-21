"""Context abstraction for CLI vs Web operation modes."""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any


class OperationContext(ABC):
    """Abstract base class for operation contexts."""

    @abstractmethod
    def get_current_story_identifier(self) -> Optional[str]:
        """Get the current story identifier (slug or UUID)."""
        pass

    @abstractmethod
    def set_current_story_identifier(self, identifier: str) -> None:
        """Set the current story identifier."""
        pass

    @abstractmethod
    def clear_current_story(self) -> None:
        """Clear the current story selection."""
        pass


class CLIContext(OperationContext):
    """CLI operation context with file-based active story tracking."""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.snowmeth_dir = self.project_dir / ".snowmeth"
        self.config_file = self.snowmeth_dir / "config.json"

        # Ensure directory exists
        self.snowmeth_dir.mkdir(parents=True, exist_ok=True)

        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load CLI configuration."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {"current_story": None}

    def _save_config(self) -> None:
        """Save CLI configuration."""
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def get_current_story_identifier(self) -> Optional[str]:
        """Get the current story identifier (slug for CLI compatibility)."""
        return self._config.get("current_story")

    def set_current_story_identifier(self, identifier: str) -> None:
        """Set the current story identifier."""
        self._config["current_story"] = identifier
        self._save_config()

    def clear_current_story(self) -> None:
        """Clear the current story selection."""
        self._config["current_story"] = None
        self._save_config()


class WebContext(OperationContext):
    """Web operation context with explicit story specification."""

    def __init__(self, story_id: str, user_id: Optional[str] = None):
        self.story_id = story_id
        self.user_id = user_id

    def get_current_story_identifier(self) -> Optional[str]:
        """Get the current story identifier (UUID for web)."""
        return self.story_id

    def set_current_story_identifier(self, identifier: str) -> None:
        """Set the current story identifier (no-op for web - context is immutable)."""
        # In web context, each request has its own context
        # This is a no-op since web contexts are request-scoped
        pass

    def clear_current_story(self) -> None:
        """Clear the current story selection (no-op for web)."""
        # In web context, each request has its own context
        # This is a no-op since web contexts are request-scoped
        pass


class StatelessContext(OperationContext):
    """Stateless context for operations that don't need active story tracking."""

    def __init__(self, story_identifier: Optional[str] = None):
        self.story_identifier = story_identifier

    def get_current_story_identifier(self) -> Optional[str]:
        """Get the story identifier."""
        return self.story_identifier

    def set_current_story_identifier(self, identifier: str) -> None:
        """Set the story identifier."""
        self.story_identifier = identifier

    def clear_current_story(self) -> None:
        """Clear the story identifier."""
        self.story_identifier = None
