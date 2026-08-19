from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ExportFormat(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"


@dataclass(frozen=True)
class DocumentRef:
    document_id: str


@dataclass(frozen=True)
class EditProposal:
    proposal_id: str
    document_id: str
    proposed_changes: Dict[str, str]
    status: str


@dataclass(frozen=True)
class ApprovalResult:
    proposal_id: str
    status: str
    applied: bool


@dataclass(frozen=True)
class ExportArtifact:
    format: ExportFormat
    reference: str


@dataclass(frozen=True)
class ExportResult:
    document_id: str
    artifacts: List[ExportArtifact]
    status: str