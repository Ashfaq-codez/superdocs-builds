from pathlib import Path
from typing import Dict

from backend.models.domain import ComposerRecord
from backend.services.jurisdiction import JurisdictionEngine
from backend.services.templating import TemplateEngine
from backend.services.orchestrator import ComposerOrchestrator

from superdocs_client.mock_client import MockSuperDocsClient


# Global singletons for in-memory execution
GLOBAL_STATE_STORE: Dict[str, ComposerRecord] = {}
MOCK_SDK_INSTANCE = MockSuperDocsClient()

# Resolve paths
TEMPLATES_BASE_PATH = Path(__file__).parent.parent.parent / "templates"

_jurisdiction_engine = JurisdictionEngine()
_template_engine = TemplateEngine()

def get_orchestrator() -> ComposerOrchestrator:
    return ComposerOrchestrator(
        jurisdiction_engine=_jurisdiction_engine,
        template_engine=_template_engine,
        superdocs_client=MOCK_SDK_INSTANCE,
        state_store=GLOBAL_STATE_STORE,
        templates_base_path=TEMPLATES_BASE_PATH
    )