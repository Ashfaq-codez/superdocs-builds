"""Domain exception hierarchy for the HR Composer Backend."""

class HRComposerError(Exception):
    """Base exception for all HR Composer domain errors."""
    pass

class UnsupportedJurisdictionError(HRComposerError):
    """Raised when a location cannot be mapped to a supported jurisdiction."""
    pass

class MissingTemplateFieldError(HRComposerError):
    """Raised when an HRRecord is missing a field required by the TemplateDefinition."""
    pass

class ConfigurationError(HRComposerError):
    """Raised when template registries or files are missing/malformed."""
    pass

class ComposerNotFoundError(HRComposerError):
    """Raised when a requested composition ID does not exist."""
    pass

class InvalidStateTransitionError(HRComposerError):
    """Raised when a lifecycle transition is forbidden."""
    pass