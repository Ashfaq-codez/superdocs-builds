from pathlib import Path
from typing import Dict

from backend.models.domain import AssemblyRecord
from backend.services.resolver import ClauseResolver
from backend.services.assembler import AssemblyEngine
from backend.services.adapter import SuperDocsAdapter
from backend.services.orchestrator import OrchestrationService

from superdocs_client.mock_client import MockSuperDocsClient


# Global in-memory state stores for the application lifecycle
GLOBAL_STATE_STORE: Dict[str, AssemblyRecord] = {}

# We instantiate the Mock SDK globally so it retains its uploaded documents/proposals across requests
MOCK_SDK_INSTANCE = MockSuperDocsClient()

# The resolver requires the path to the clause library.
# In a real app, this might come from an environment variable. 
# For this build, we point it to the local clause_library folder.
LIBRARY_BASE_PATH = Path(__file__).parent.parent.parent / "clause_library"

# Instantiate stateless domain services
_resolver = ClauseResolver(library_base_path=LIBRARY_BASE_PATH)
_assembler = AssemblyEngine()
_adapter = SuperDocsAdapter()


def get_orchestrator() -> OrchestrationService:
    """FastAPI Dependency providing the configured orchestration service."""
    return OrchestrationService(
        resolver=_resolver,
        assembler=_assembler,
        adapter=_adapter,
        superdocs_client=MOCK_SDK_INSTANCE,
        state_store=GLOBAL_STATE_STORE
    )