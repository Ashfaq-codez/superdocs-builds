from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AssemblyState(str, Enum):
    """Tracks the lifecycle of an assembly request."""
    ASSEMBLING = "ASSEMBLING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPORTED = "EXPORTED"


class FormattingHints(BaseModel):
    """Metadata to ensure consistent formatting across assembled documents."""
    style: str
    page_break_before: bool = False


class ClauseDefinition(BaseModel):
    """Represents a reusable, distinct legal/document block."""
    id: str
    version: str
    title: str
    body: str
    formatting_hints: FormattingHints


class AssemblyRequest(BaseModel):
    """Client request detailing the exact deterministic order of clauses."""
    clause_ids: List[str] = Field(..., min_length=1)


class AssemblyRecord(BaseModel):
    """Internal orchestration model tracking local workflow and SuperDocs SDK references."""
    assembly_id: str
    status: AssemblyState = AssemblyState.ASSEMBLING
    requested_clauses: List[str]
    
    # SuperDocs external integration references
    document_id: Optional[str] = None
    proposal_id: Optional[str] = None
    
    # Stores abstract artifacts retrieved after successful export
    artifacts: Optional[List[Dict[str, str]]] = None
    
class AssembledSection(BaseModel):
    """A normalized, structured representation of an assembled block."""
    source_clause_id: str
    title: str
    paragraphs: List[str]
    page_break_before: bool

class AssembledDocument(BaseModel):
    """The pure, intermediate representation of the assembled document."""
    sections: List[AssembledSection]