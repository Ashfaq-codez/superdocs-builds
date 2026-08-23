from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.models.domain import HRRecord
from superdocs_client.models import ExportFormat


class ComposeRequest(BaseModel):
    """Payload sent by the Word Add-in to start generation."""
    hr_record: HRRecord


class ExportRequest(BaseModel):
    """Payload to trigger export after human approval."""
    formats: List[ExportFormat]


class ComposerResponse(BaseModel):
    """The public representation of a composition, hiding internal bodies but showing provenance."""
    composition_id: str
    status: str
    jurisdiction_applied: Optional[str] = None
    template_id_applied: Optional[str] = None
    document_id: Optional[str] = None
    artifacts: Optional[List[Dict[str, Any]]] = None