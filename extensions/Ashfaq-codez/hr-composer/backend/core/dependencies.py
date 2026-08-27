from pathlib import Path
from typing import Dict

from backend.models.domain import ComposerRecord
from backend.services.jurisdiction import JurisdictionEngine
from backend.services.templating import TemplateEngine
from backend.services.orchestrator import ComposerOrchestrator

# NEW: Import the real local client
from superdocs_client.local_client import LocalSuperDocsClient 

# Global state and paths
GLOBAL_STATE_STORE: Dict[str, ComposerRecord] = {}

BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_BASE_PATH = BASE_DIR / "templates"
RUNTIME_ARTIFACTS_DIR = BASE_DIR / "runtime" / "artifacts"

# NEW: Initialize the real local client
LOCAL_SDK_INSTANCE = LocalSuperDocsClient(runtime_dir=RUNTIME_ARTIFACTS_DIR)

_jurisdiction_engine = JurisdictionEngine()
_template_engine = TemplateEngine()

def get_orchestrator() -> ComposerOrchestrator:
    return ComposerOrchestrator(
        jurisdiction_engine=_jurisdiction_engine,
        template_engine=_template_engine,
        superdocs_client=LOCAL_SDK_INSTANCE, # <-- Now using real physical generator
        state_store=GLOBAL_STATE_STORE,
        templates_base_path=TEMPLATES_BASE_PATH
    )