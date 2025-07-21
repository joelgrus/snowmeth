"""Custom exceptions for the Snowflake Method application."""


class SnowmethError(Exception):
    """Base exception for all Snowmeth errors."""

    pass


class StoryError(SnowmethError):
    """Base exception for story-related errors."""

    pass


class StoryNotFoundError(StoryError):
    """Raised when a requested story cannot be found."""

    pass


class StoryAlreadyExistsError(StoryError):
    """Raised when trying to create a story that already exists."""

    pass


class ConfigurationError(SnowmethError):
    """Raised when there are configuration issues."""

    pass


class ModelError(SnowmethError):
    """Raised when there are model-related issues."""

    pass


class WorkflowError(SnowmethError):
    """Raised when there are workflow progression issues."""

    pass


class StepAdvancementError(WorkflowError):
    """Raised when a step cannot be advanced."""

    pass
