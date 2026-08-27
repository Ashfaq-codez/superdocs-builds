from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class Jurisdiction(str, Enum):
    CALIFORNIA = "CALIFORNIA"
    UK = "UK"
    STANDARD = "STANDARD"


class HRRecord(BaseModel):
    candidate_name: str
    role: str
    salary: str
    location: str
    start_date: str
    benefits: str  # <--- ADD THIS LINE
    employment_type: Optional[str] = None # (Keep this if you already have it)


class TemplateDefinition(BaseModel):
    """Defines a template's requirements and raw body."""
    id: str
    version: str
    jurisdiction: Jurisdiction
    required_fields: List[str]
    body_template: str


class ComposedDocument(BaseModel):
    """The populated document with strict provenance."""
    template_id: str
    template_version: str
    jurisdiction: Jurisdiction
    body: str


class ComposerState(str, Enum):
    COMPOSING = "COMPOSING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"


class ComposerRecord(BaseModel):
    """Internal orchestration model for the composer lifecycle."""
    composition_id: str
    status: ComposerState
    hr_record: HRRecord
    
    # Populated during the composing phase
    composed_document: Optional[ComposedDocument] = None
    
    # SuperDocs external integration references
    document_id: Optional[str] = None
    proposal_id: Optional[str] = None
    artifacts: Optional[List[Dict[str, Any]]] = None