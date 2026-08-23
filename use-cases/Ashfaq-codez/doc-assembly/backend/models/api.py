from typing import List
from pydantic import BaseModel, Field
from superdocs_client.models import ExportFormat


class AssembleRequest(BaseModel):
    """Payload for initiating a document assembly."""
    clause_ids: List[str] = Field(..., min_length=1, description="Ordered list of clause IDs to assemble.")


class ExportRequest(BaseModel):
    """Payload for exporting an approved assembly."""
    formats: List[ExportFormat] = Field(..., min_length=1, description="List of formats to export (e.g., PDF, DOCX).")