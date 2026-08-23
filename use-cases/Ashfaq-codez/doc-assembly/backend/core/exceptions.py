"""Domain exception hierarchy for the Document-Assembly Microservice."""

class DocAssemblyError(Exception):
    """Base exception for all document assembly domain errors."""
    pass

class ClauseResolutionError(DocAssemblyError):
    """Base exception for all failures occurring during clause resolution."""
    pass

class InvalidRequestError(ClauseResolutionError):
    """Raised when the input list is empty or contains blank IDs."""
    pass

class ClauseNotFoundError(ClauseResolutionError):
    """Raised when a requested clause ID does not exist in the registry."""
    pass

class LibraryConfigurationError(ClauseResolutionError):
    """Raised when the library state is invalid (missing file, bad JSON, unsafe path, etc.)."""
    pass

class AssemblyError(DocAssemblyError):
    """Base exception for document assembly errors."""
    pass

class EmptyAssemblyError(AssemblyError):
    """Raised when the assembly engine is given an empty list of clauses."""
    pass

class ClauseFormatError(AssemblyError):
    """Raised when a clause violates strict deterministic formatting rules."""
    pass

class AssemblyNotFoundError(DocAssemblyError):
    """Raised when an orchestration operation requests an unknown assembly_id."""
    pass

class InvalidStateTransitionError(DocAssemblyError):
    """Raised when a lifecycle transition is forbidden (e.g., export before approval)."""
    pass